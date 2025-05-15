import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import requests
import time

API_URL = "http://localhost:8000"

class VideoAnalyzer(VideoTransformerBase):
    def __init__(self):
        self.last_sent_time = 0
        self.send_interval = 3  # seconds

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        current_time = time.time()
        if current_time - self.last_sent_time > self.send_interval:
            self.last_sent_time = current_time

            _, buffer = cv2.imencode(".jpg", img)
            jpg_bytes = buffer.tobytes()

            try:
                response = requests.post(
                    f"{API_URL}/analyze_frame/",
                    files={"file": ("frame.jpg", jpg_bytes, "image/jpeg")},
                    data={"user_id": st.session_state.username}
                )
                if response.status_code == 200:
                    st.session_state.last_analysis = response.json()
            except Exception as e:
                print(f"Error sending frame: {e}")

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def live_analysis_page():
    st.subheader("🎥 Live Interview Monitoring")

    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = None

    st.info("👁 Webcam feed is live. Analysis runs every few seconds.")

    webrtc_streamer(
        key="live-monitor",
        video_processor_factory=VideoAnalyzer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    result = st.session_state.last_analysis
    if result:
        st.markdown("### 🧠 Latest Analysis")
        if not result["result"]["detections"]:
            st.success("🟢 No suspicious behavior detected")
        else:
            for detection in result["result"]["detections"]:
                if detection["detected"]:
                    st.warning(
                        f"⚠️ {detection['flag'].replace('_', ' ').title()} "
                        f"(Confidence: {detection['confidence']*100:.1f}%)"
                    )
