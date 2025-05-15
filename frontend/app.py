import streamlit as st
from pages.face_verify import face_verification_page
from pages.interview_session import interview_session_page
#from pages.code_evaluation import code_evaluation_page
#from pages.final_report import final_report_page

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(page_title="AI Interview Platform", layout="centered")

# ------------------ SESSION STATE INIT ------------------ #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "face_verified" not in st.session_state:
    st.session_state.face_verified = False

# ------------------ LOGIN FLOW ------------------ #
if not st.session_state.logged_in:
    st.title("🧠 AI Interview Platform Login")
    username = st.text_input("Enter your name to begin:")
    if st.button("Start"):
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.face_verified = False
        else:
            st.warning("Please enter a valid name.")

# ------------------ FACE VERIFICATION ------------------ #
elif not st.session_state.face_verified:
    st.info(f"👋 Welcome, {st.session_state.username}. Please complete face verification to continue.")
    face_verification_page()

# ------------------ MAIN APPLICATION ------------------ #
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    page = st.sidebar.radio("Navigation", ["Interview Session", "Code Evaluation", "Final Report"])

    if page == "Interview Session":
        interview_session_page()
    #elif page == "Code Evaluation":
    #    code_evaluation_page()
    #elif page == "Final Report":
    #    final_report_page()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
