import streamlit as st
import whisper
import os
import pandas as pd
import numpy as np
from src.auth_manager import AuthManager
from src.db_manager import DatabaseManager
from src.kb_generator import process_document_to_kb
from sentence_transformers import SentenceTransformer, util

# --- PAGE CONFIG ---
st.set_page_config(page_title="Edu-Analytics Platform", layout="wide", page_icon="🎓")

# --- MODEL & MANAGER INITIALIZATION ---
@st.cache_resource
def load_resources():
    auth_man = AuthManager()
    db_man = DatabaseManager()
    w_model = whisper.load_model("base")
    s_model = SentenceTransformer('all-MiniLM-L6-v2')
    return auth_man, db_man, w_model, s_model

auth, db, whisper_model, similarity_model = load_resources()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION INTERFACE ---
if st.session_state.user is None:
    st.title("🎓 Concept Gap Detection System")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab2:
        st.subheader("Create New Account")
        new_email = st.text_input("Email", key="reg_email")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        name = st.text_input("Full Name")
        role = st.selectbox("I am a...", ["student", "faculty"])
        if st.button("Register"):
            success, msg = auth.sign_up(new_email, new_pass, name, role)
            st.info(msg)

    with tab1:
        st.subheader("Welcome Back")
        email = st.text_input("Email", key="log_email")
        pw = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            success, msg = auth.login(email, pw)
            if success: st.rerun()
            else: st.error(msg)

# --- MAIN APPLICATION (LOGGED IN) ---
else:
    st.sidebar.title(f"👤 {st.session_state.role.capitalize()}")
    st.sidebar.write(f"**{st.session_state.user.email}**")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    # --- FACULTY VIEW ---
    if st.session_state.role == "faculty":
        st.header("👨‍🏫 Faculty Dashboard")
        manage_tab, analytics_tab = st.tabs(["📚 Manage Subjects", "📊 Class Analytics"])

        with manage_tab:
            col1, col2 = st.columns([1, 2])
            with col1:
                with st.expander("➕ Create New Subject", expanded=True):
                    sub_name = st.text_input("Subject Name")
                    if st.button("Create"):
                        db.create_subject(sub_name, st.session_state.user.id)
                        st.success("Subject Added!")
                        st.rerun()
            
            with col2:
                st.subheader("Upload Learning Materials")
                my_subs = db.get_faculty_subjects(st.session_state.user.id).data
                if my_subs:
                    sub_map = {s['name']: s['id'] for s in my_subs}
                    target = st.selectbox("Select Subject", list(sub_map.keys()))
                    file = st.file_uploader("Upload PDF/PPTX", type=['pdf', 'pptx'])
                    if file and st.button("Generate Knowledge Base"):
                        with st.spinner("AI analyzing document..."):
                            with open("temp.pdf", "wb") as f: f.write(file.getbuffer())
                            kb_data = process_document_to_kb("temp.pdf", target)
                            if kb_data:
                                db.save_knowledge_base(sub_map[target], kb_data)
                                st.success("Knowledge Base Live!")
                            else: st.error("AI failed to extract concepts.")
                else: st.info("Create a subject first.")

        with analytics_tab:
            st.subheader("Student Performance Overview")
            raw_data = db.get_faculty_analytics(st.session_state.user.id).data
            if raw_data:
                # Flattening for Pandas
                data = [{"Subject": r['knowledge_base']['subjects']['name'], 
                         "Concept": r['knowledge_base']['concept_name'], 
                         "Score": r['eqs_score']} for r in raw_data]
                df = pd.DataFrame(data)
                
                # Concept Mastery Chart
                avg_scores = df.groupby("Concept")["Score"].mean().sort_values()
                st.bar_chart(avg_scores)
                
                # Gap Detection
                st.write("### 🚨 Critical Gaps")
                gaps = avg_scores[avg_scores < 60]
                if not gaps.empty:
                    for c, s in gaps.items():
                        st.warning(f"Low Mastery in **{c}** (Avg: {round(s,1)}%)")
                else: st.success("All concepts are being mastered well!")
            else: st.info("No student attempts recorded yet.")

    # --- STUDENT VIEW ---
    else:
        st.header("✍️ Student Arena")
        dash_tab, practice_tab = st.tabs(["📊 My Progress", "🚀 Practice"])

        with dash_tab:
            st.subheader("Your Learning Curve")
            history = db.get_student_attempts(st.session_state.user.id).data
            if history:
                hdf = pd.DataFrame(history)
                hdf['Date'] = pd.to_datetime(hdf['created_at']).dt.date
                
                st.line_chart(hdf.set_index('Date')['eqs_score'])
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Avg Score", f"{round(hdf['eqs_score'].mean(),1)}%")
                m2.metric("Attempts", len(hdf))
                m3.metric("Best", f"{hdf['eqs_score'].max()}%")
                
                st.write("### History")
                st.dataframe(hdf[['Date', 'eqs_score', 'transcript']].tail(10))
            else: st.info("Start practicing to see your data here!")

        with practice_tab:
            # Enrollment
            with st.expander("📚 Enroll in New Course"):
                all_subs = db.get_all_subjects().data
                if all_subs:
                    sub_opts = {f"{s['name']} ({s['profiles']['full_name']})": s['id'] for s in all_subs}
                    target = st.selectbox("Choose Subject", list(sub_opts.keys()))
                    if st.button("Enroll"):
                        db.enroll_student(st.session_state.user.id, sub_opts[target])
                        st.success("Enrolled!")
                        st.rerun()

            # Practice Logic
            enrolled = db.get_student_enrollments(st.session_state.user.id).data
            if enrolled:
                u_subs = {e['subjects']['name']: e['subject_id'] for e in enrolled}
                active = st.selectbox("Practice Subject", list(u_subs.keys()))
                concepts = db.get_concepts_for_subject(u_subs[active]).data
                
                if concepts:
                    c_map = {c['concept_name']: c for c in concepts}
                    sel_c = st.selectbox("Choose Topic", list(c_map.keys()))
                    target_c = c_map[sel_c]
                    
                    st.info(f"Target: **{sel_c}**")
                    audio = st.file_uploader("Upload Audio", type=['wav', 'mp3'])
                    
                    if audio and st.button("Analyze My Speech"):
                        with st.spinner("AI Scoring..."):
                            with open("temp_audio.wav", "wb") as f: f.write(audio.getbuffer())
                            res = whisper_model.transcribe("temp_audio.wav")
                            text = res['text']
                            
                            # Scoring
                            e1 = similarity_model.encode(text, convert_to_tensor=True)
                            e2 = similarity_model.encode(target_c['ideal_answer'], convert_to_tensor=True)
                            sim = float(util.pytorch_cos_sim(e1, e2)[0][0])
                            
                            found = [k for k in target_c['keywords'] if k.lower() in text.lower()]
                            miss = [k for k in target_c['keywords'] if k.lower() not in text.lower()]
                            score = (sim * 40) + ((len(found)/len(target_c['keywords'])) * 60)
                            
                            # Save
                            db.save_attempt({
                                "student_id": st.session_state.user.id,
                                "concept_id": target_c['id'],
                                "transcript": text,
                                "similarity_score": round(sim, 2),
                                "eqs_score": round(score, 2),
                                "missing_keywords": miss
                            })
                            
                            st.subheader(f"Score: {round(score,1)}/100")
                            if miss: st.warning(f"Missed terms: {', '.join(miss)}")
                            else: st.success("Perfect terminology!")
                else: st.warning("No concepts uploaded for this course yet.")