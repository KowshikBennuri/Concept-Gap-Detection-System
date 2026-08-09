from supabase import create_client, Client
import streamlit as st

class DatabaseManager:
    def __init__(self):
        # Ensure these are defined in your .streamlit/secrets.toml
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        self.supabase: Client = create_client(url, key)

    # --- SUBJECT MANAGEMENT ---
    def create_subject(self, name, faculty_id):
        data = {"name": name, "faculty_id": faculty_id}
        return self.supabase.table("subjects").insert(data).execute()

    def get_faculty_subjects(self, faculty_id):
        return self.supabase.table("subjects").select("*").eq("faculty_id", faculty_id).execute()

    def get_all_subjects(self):
        # Select subjects and join with profiles to get the Faculty Name
        return self.supabase.table("subjects").select("*, profiles(full_name)").execute()

    # --- KNOWLEDGE BASE MANAGEMENT ---
    def save_knowledge_base(self, subject_id, concept_list):
        for concept in concept_list:
            concept["subject_id"] = subject_id
            self.supabase.table("knowledge_base").insert(concept).execute()

    def get_concepts_for_subject(self, subject_id):
        return self.supabase.table("knowledge_base").select("*").eq("subject_id", subject_id).execute()

    # --- ENROLLMENT & ATTEMPTS ---
    def enroll_student(self, student_id, subject_id):
        data = {"student_id": student_id, "subject_id": subject_id}
        return self.supabase.table("enrollments").insert(data).execute()

    def get_student_enrollments(self, student_id):
        # Joins enrollments with subjects to show the course names to the student
        return self.supabase.table("enrollments").select("*, subjects(name)").eq("student_id", student_id).execute()

    def save_attempt(self, attempt_data):
        return self.supabase.table("attempts").insert(attempt_data).execute()

    # --- DASHBOARD & ANALYTICS (NEW) ---
    def get_student_attempts(self, student_id):
        """
        Fetches all previous attempts for a specific student.
        Joins with knowledge_base to show the name of the topic they practiced.
        """
        return self.supabase.table("attempts") \
            .select("*, knowledge_base(concept_name)") \
            .eq("student_id", student_id) \
            .order("created_at", desc=True) \
            .execute()

    def get_faculty_analytics(self, faculty_id):
        """
        Fetches all student attempts for all subjects owned by a specific faculty.
        This uses a nested join: attempts -> knowledge_base -> subjects.
        """
        return self.supabase.table("attempts") \
            .select("""
                *,
                knowledge_base!inner(
                    concept_name,
                    subjects!inner(name, faculty_id)
                )
            """) \
            .eq("knowledge_base.subjects.faculty_id", faculty_id) \
            .execute()
    
    # --- ADD THIS TO DatabaseManager CLASS ---
    def delete_concept(self, concept_id):
        """
        Allows faculty to remove a specific concept from the knowledge base.
        """
        return self.supabase.table("knowledge_base").delete().eq("id", concept_id).execute()