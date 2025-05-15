import streamlit as st
from utils.helpers import encode_image, send_verification_request

API_URL = "http://localhost:8000"

def face_verification_page():
    st.header("🔐 Face Registration & Live Face Verification")

    user_id = st.text_input("👤 Enter Username")

    reg_img = st.file_uploader("Upload Registered Image", type=["jpg", "jpeg", "png"])
    cam_img = st.camera_input("📸 Capture Your Live Face")

    if st.button("🚀 Verify Face"):
        if not (user_id and reg_img and cam_img):
            st.warning("Please enter username, upload registered face, and capture live image.")
            return

        with st.spinner("Verifying faces..."):
            reg_b64 = encode_image(reg_img)
            cap_b64 = encode_image(cam_img)
            result = send_verification_request(user_id, reg_b64, cap_b64, API_URL)

        if result["status"] == "verified":
            st.success(f"✅ Face Verified! Confidence: {result.get('confidence', 0)*100:.2f}%")
            st.session_state.face_verified = True
            st.rerun()
        elif result["status"] == "not_verified":
            st.error("❌ Face did not match.")
        else:
            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
