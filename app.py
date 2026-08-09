import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers.utils.generic")
warnings.filterwarnings("ignore", message="Accessing `__path__` *")
import streamlit as st
import whisper
import os
import pandas as pd
import numpy as np
from src.auth_manager import AuthManager
from src.db_manager import DatabaseManager
from src.kb_generator import process_document_to_kb

# --- RESEARCH ENGINE INTEGRATION ---
from src.audio_utils import perform_initial_guard
from src.evaluator import ConceptEvaluator

# --- GLOBAL CONFIGURATION ---
st.set_page_config(page_title="Edu-Analytics Research Platform", layout="wide", page_icon="🎓")

# --- PERSISTENT RESOURCE ALLOCATION ---
@st.cache_resource
def load_resources():
    auth_man = AuthManager()
    db_man = DatabaseManager()
    w_model = whisper.load_model("base")
    eval_man = ConceptEvaluator()
    return auth_man, db_man, w_model, eval_man

auth, db, whisper_model, evaluator = load_resources()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION MODULE ---
if st.session_state.user is None:
    st.title("🎓 Concept Gap Detection System")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab2:
        st.subheader("Account Registration")
        new_email = st.text_input("Email Address", key="reg_email")
        new_pass = st.text_input("Security Password", type="password", key="reg_pass")
        name = st.text_input("Full Name")
        role = st.selectbox("Institutional Role", ["student", "faculty"])
        if st.button("Register"):
            success, msg = auth.sign_up(new_email, new_pass, name, role)
            st.info(msg)

    with tab1:
        st.subheader("Secure Access")
        email = st.text_input("Email", key="log_email")
        pw = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            success, msg = auth.login(email, pw)
            if success: st.rerun()
            else: st.error(msg)

# --- PROTECTED APPLICATION CORE ---
else:
    st.sidebar.title(f"👤 {st.session_state.role.capitalize()}")
    st.sidebar.write(f"**User:** {st.session_state.user.email}")
    
    if st.sidebar.button("System Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    # --- FACULTY ADMINISTRATION & ANALYTICS ---
    if st.session_state.role == "faculty":
        st.header("👨‍🏫 Faculty Research Dashboard")
        manage_tab, analytics_tab = st.tabs(["📚 Knowledge Base", "📊 Research Analytics"])

        with manage_tab:
            col1, col2 = st.columns([1, 2])
            with col1:
                with st.expander("➕ Subject Creation", expanded=True):
                    sub_name = st.text_input("Subject Name")
                    if st.button("Initialize Subject"):
                        db.create_subject(sub_name, st.session_state.user.id)
                        st.success("Subject Registered.")
                        st.rerun()
            
            with col2:
                st.subheader("Curriculum Content Ingestion")
                my_subs = db.get_faculty_subjects(st.session_state.user.id).data
                if my_subs:
                    sub_map = {s['name']: s['id'] for s in my_subs}
                    target = st.selectbox("Select Active Subject", list(sub_map.keys()))
                    file = st.file_uploader("Upload PPTX/PDF (Numerical/Formula parsing enabled)", type=['pdf', 'pptx'])
                    if file and st.button("Generate Knowledge Base"):
                        with st.spinner("AI parsing technical content and formulas..."):
                            with open("temp.pdf", "wb") as f: f.write(file.getbuffer())
                            kb_data = process_document_to_kb("temp.pdf", target)
                            if kb_data:
                                db.save_knowledge_base(sub_map[target], kb_data)
                                st.success("Knowledge base populated with technical alignment.")
                            else: st.error("AI extraction failure.")
                else: st.info("Initialize a subject to begin ingestion.")

        with analytics_tab:
            st.subheader("📊 Comparative Model Analytics (Backend View)")
            raw_data = db.get_faculty_analytics(st.session_state.user.id).data
            if raw_data:
                # Processing research metrics for display (Matching your exact SQL Schema)
                display_df = pd.DataFrame([{
                    "Timestamp": r['created_at'][:16].replace('T', ' '),
                    "Concept": r['knowledge_base']['concept_name'],
                    "EQS Final": r['eqs_score'],
                    "TF-IDF": r['tfidf_score'],
                    "MPNET": r['mpnet_score'],
                    "RoBERTa": r['roberta_score'],
                    "BERTScore": r['bert_score'],
                    "ROUGE-1": r['rouge1'],
                    "ROUGE-2": r['rouge2'],
                    "ROUGE-L": r['rouge_l']
                } for r in raw_data])
                
                st.write("### Model Performance Comparison")
                st.dataframe(display_df, use_container_width=True)
                
                st.write("### Classroom Mastery Distribution")
                avg_scores = display_df.groupby("Concept")["EQS Final"].mean().sort_values()
                st.bar_chart(avg_scores)
            else: st.info("No comparative analytics recorded yet.")

    # --- STUDENT LEARNING INTERFACE ---
    else:
        st.header("✍️ Student Mastery Arena")
        dash_tab, practice_tab = st.tabs(["📊 Performance History", "🚀 Concept Practice"])

        with dash_tab:
            st.subheader("Learning Progress Visualization")
            history = db.get_student_attempts(st.session_state.user.id).data
            if history:
                hdf = pd.DataFrame(history)
                hdf['Date'] = pd.to_datetime(hdf['created_at']).dt.date
                st.line_chart(hdf.set_index('Date')['eqs_score'])
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Average Mastery", f"{round(hdf['eqs_score'].mean(),1)}%")
                m2.metric("Total Sessions", len(hdf))
                m3.metric("Peak Score", f"{hdf['eqs_score'].max()}%")
                
                st.write("### Recent Activity Logs")
                st.dataframe(hdf[['Date', 'eqs_score', 'transcript']].tail(10))
            else: st.info("Submit an attempt to view progress metrics.")

        with practice_tab:
            with st.expander("📚 Course Enrollment"):
                all_subs = db.get_all_subjects().data
                if all_subs:
                    sub_opts = {f"{s['name']} ({s['profiles']['full_name']})": s['id'] for s in all_subs}
                    target = st.selectbox("Select Available Course", list(sub_opts.keys()))
                    if st.button("Confirm Enrollment"):
                        db.enroll_student(st.session_state.user.id, sub_opts[target])
                        st.success("Successfully enrolled.")
                        st.rerun()

            enrolled = db.get_student_enrollments(st.session_state.user.id).data
            if enrolled:
                u_subs = {e['subjects']['name']: e['subject_id'] for e in enrolled}
                active = st.selectbox("Active Subject", list(u_subs.keys()))
                concepts = db.get_concepts_for_subject(u_subs[active]).data
                
                if concepts:
                    c_map = {c['concept_name']: c for c in concepts}
                    sel_c = st.selectbox("Select Practice Topic", list(c_map.keys()))
                    target_c = c_map[sel_c]
                    
                    st.info(f"Objective: Provide a verbal explanation for **{sel_c}**.")
                    audio = st.file_uploader("Upload Vocal Response", type=['wav', 'mp3'])
                    
                    if audio and st.button("Initiate Evaluation"):
                        with st.spinner("Processing speech and validating relevance..."):
                            with open("temp_audio.wav", "wb") as f: f.write(audio.getbuffer())
                            
                            is_valid, msg, transcript = perform_initial_guard(
                                "temp_audio.wav", 
                                target_c['keywords'], 
                                whisper_model
                            )

                        if not is_valid:
                            st.error(f"Analysis Aborted: {msg}")
                        else:
                            with st.spinner("Computing comparative results..."):
                                # Execute Research-Grade Evaluator
                                comp_results = evaluator.get_comparative_scores(transcript, target_c['ideal_answer'])
                                
                                # Scoring Architecture
                                primary_sim = comp_results['mpnet_score']
                                found_keywords = [k for k in target_c['keywords'] if k.lower() in transcript.lower()]
                                missing_keywords = [k for k in target_c['keywords'] if k.lower() not in transcript.lower()]
                                coverage_ratio = len(found_keywords) / len(target_c['keywords'])
                                
                                final_score = (primary_sim * 40) + (coverage_ratio * 60)
                                
                                # PROFESSIONAL TERMINAL LOGGING (Backend Monitoring)
                                print("\n" + "="*60)
                                print(f"RESEARCH AUDIT: {sel_c}")
                                print(f"Student: {st.session_state.user.email}")
                                print("-" * 30)
                                print(f"TF-IDF (Non-DL): {comp_results['tfidf_score']:.4f}")
                                print(f"MPNET (DL-SOTA): {comp_results['mpnet_score']:.4f}")
                                print(f"RoBERTa:       {comp_results['roberta_score']:.4f}")
                                print(f"ROUGE-1:       {comp_results['rouge1']:.4f}")
                                print(f"ROUGE-L:       {comp_results['rouge_l']:.4f}")
                                print(f"BERTScore:     {comp_results['bert_score']:.4f}")
                                print("="*60 + "\n")

                                # FRONTEND: Outcome-oriented student feedback
                                st.success(f"### Final Concept Mastery: {round(final_score, 1)}/100")
                                
                                # --- IN app.py ---
# Double check that your save_attempt uses the exact same keys:
                                db.save_attempt({
                                    "student_id": st.session_state.user.id,
                                    "concept_id": target_c['id'],
                                    "transcript": transcript,
                                    "eqs_score": round(final_score, 2),
                                    "similarity_score": round(primary_sim, 2),
                                    "tfidf_score": round(comp_results['tfidf_score'], 2),
                                    "minilm_score": round(comp_results['minilm_score'], 2),
                                    "mpnet_score": round(comp_results['mpnet_score'], 2),
                                    "roberta_score": round(comp_results['roberta_score'], 2),
                                    "rouge1": round(comp_results['rouge1'], 2),  # Matches comp_results['rouge1']
                                    "rouge2": round(comp_results['rouge2'], 2),  # Matches comp_results['rouge2']
                                    "rouge_l": round(comp_results['rouge_l'], 2), # Matches comp_results['rouge_l']
                                    "bert_score": round(comp_results['bert_score'], 2),
                                    "missing_keywords": missing_keywords
                                })
                                
                                if missing_keywords: st.warning(f"Constructive Feedback: Consider including terms like {', '.join(missing_keywords)} to improve alignment.")
                                else: st.success("Technical terminology alignment optimal.")
                else: st.warning("Subject content pending faculty upload.")