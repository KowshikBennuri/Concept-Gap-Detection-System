from supabase import create_client
import streamlit as st

class AuthManager:
    def __init__(self):
        self.supabase = create_client(
            st.secrets["SUPABASE_URL"], 
            st.secrets["SUPABASE_KEY"]
        )

    def sign_up(self, email, password, full_name, role):
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password})
            if res.user:
                user_data = {"id": res.user.id, "full_name": full_name, "role": role}
                self.supabase.table("profiles").insert(user_data).execute()
                return True, "Account created! Verify your email to login."
        except Exception as e:
            return False, str(e)
        return False, "Signup failed."

    def login(self, email, password):
        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                # Use .maybe_single() instead of .single() to avoid the crash if 0 rows exist
                profile_res = self.supabase.table("profiles").select("role").eq("id", res.user.id).maybe_single().execute()
                
                if profile_res.data:
                    st.session_state.user = res.user
                    st.session_state.role = profile_res.data['role']
                    return True, "Success!"
                else:
                    return False, "User authenticated but profile not found. Please re-register."
        except Exception as e:
            return False, str(e)
        return False, "Login failed."