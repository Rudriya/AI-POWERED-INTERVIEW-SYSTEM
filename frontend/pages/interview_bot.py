import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import time
import cv2
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.interview_bot import generate_questions, evaluate_answer
from backend.services.emotion_analysis import analyze_emotion  # You must have this service

# ---- Setup session variables ----
if "questions" not in st.session_state:
    st.session_state.questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "scores" not in st.session_state:
    st.session_state.scores = []
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []
if "last_emotion" not in st.session_state:
    st.session_state.last_emotion = {"emotion": "unknown", "confidence": 0.0}


class VideoAnalyzer(VideoTransformerBase):
    def __init__(self):
        self.last_sent_time = 0
        self.send_interval = 3

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        current_time = time.time()
        if current_time - self.last_sent_time > self.send_interval:
            self.last_sent_time = current_time
            try:
                emotion_result = analyze_emotion(img)
                st.session_state.last_emotion = emotion_result
            except Exception as e:
                st.session_state.last_emotion = {"emotion": "error", "confidence": 0.0, "error": str(e)}

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def interview_bot_page():
    st.header("🎤 AI Interview Bot with Emotion Detection")

    # 🎯 Select topic and start interview
    if not st.session_state.questions:
        topic = st.selectbox("Choose a topic", ["Python", "SQL", "Machine Learning", "Data Structures"])
        if st.button("Start Interview"):
            st.session_state.questions = generate_questions(topic, count=3)
            st.rerun()
        return

    # 📸 Start webcam for emotion tracking
    st.markdown("### 👁 Live Emotion Detection During Answering")
    webrtc_streamer(
        key="emotion-monitor",
        video_processor_factory=VideoAnalyzer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    emotion = st.session_state.last_emotion
    st.markdown(f"**Detected Emotion:** `{emotion['emotion'].title()}` ({emotion['confidence']:.1f}%)")

    # 🧠 Show the current question
    if st.session_state.q_index < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.q_index]
        st.markdown(f"**Question {st.session_state.q_index + 1}:** {q}")
        answer = st.text_area("Your Answer")

        if st.button("Submit Answer"):
            with st.spinner("Evaluating your answer..."):
                feedback = evaluate_answer(q, answer)
                st.session_state.feedbacks.append(feedback)
                score_line = [line for line in feedback.split("\n") if "score" in line.lower()]
                score = int(''.join(filter(str.isdigit, score_line[0]))) if score_line else 0
                st.session_state.scores.append(score)
                st.session_state.q_index += 1
                st.rerun()
    else:
        st.success("✅ Interview Completed!")
        avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
        st.metric("Average Score", f"{avg_score:.1f} / 10")

        for i, (q, fb) in enumerate(zip(st.session_state.questions, st.session_state.feedbacks), 1):
            with st.expander(f"Q{i}: {q}"):
                st.text(fb)

        st.download_button(
            label="📥 Download Feedback",
            data="\n\n".join(st.session_state.feedbacks),
            file_name="interview_feedback.txt",
            mime="text/plain"
        )
