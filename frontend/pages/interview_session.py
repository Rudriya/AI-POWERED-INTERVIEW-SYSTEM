import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import time
import cv2
import threading
from collections import deque
import speech_recognition as sr
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.services.interview_bot import generate_questions, evaluate_answer
from deepface import DeepFace

# ---------------- EMOTION QUEUE ---------------- #
emotion_queue = deque(maxlen=1)
flag_queue = deque(maxlen=1)

# ---------------- VIDEO MONITOR CLASS ---------------- #
class EmotionMonitor(VideoTransformerBase):
    def __init__(self):
        self.last_sent_time = 0
        self.send_interval = 3
        self.lock = threading.Lock()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        current_time = time.time()

        if current_time - self.last_sent_time > self.send_interval:
            self.last_sent_time = current_time
            try:
                # Emotion detection
                result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion']
                confidence = max(result[0]['emotion'].values())

                # Face count for multiple detection
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                flags = []
                if len(faces) > 1:
                    flags.append("⚠️ Multiple faces detected")

                with self.lock:
                    emotion_queue.append({"emotion": emotion, "confidence": confidence})
                    flag_queue.append(flags)
            except Exception as e:
                print("[DeepFace Error]", e)
                emotion_queue.append({"emotion": "unknown", "confidence": 0.0})
                flag_queue.append(["⚠️ Emotion analysis failed"])

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------------- SPEECH RECOGNITION ---------------- #
def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)
        st.success("✅ Speech recognized.")
        return text
    except Exception as e:
        st.error(f"Speech recognition failed: {e}")
        return ""

# ---------------- MAIN PAGE FUNCTION ---------------- #
def interview_session_page():
    st.title("🎤 Interview Session with Live Emotion Monitoring")

    # State init
    defaults = {
        "questions": [],
        "q_index": 0,
        "scores": [],
        "feedbacks": [],
        "emotions": [],
        "flags": [],
        "last_emotion": {"emotion": "unknown", "confidence": 0.0}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Restart button
    if st.button("🔁 Restart Interview"):
        for key in defaults:
            st.session_state[key] = [] if isinstance(defaults[key], list) else defaults[key]
        st.rerun()

    # Start logic
    if not st.session_state.questions:
        topic = st.selectbox("Choose a topic", ["Python", "SQL", "Machine Learning", "Data Structures"])
        if st.button("Start Interview"):
            st.session_state.questions = generate_questions(topic, count=3)
            st.session_state.q_index = 0
            st.session_state.scores.clear()
            st.session_state.feedbacks.clear()
            st.session_state.emotions.clear()
            st.session_state.flags.clear()
            st.rerun()
        return

    # Webcam stream
    st.markdown("### 👁 Emotion Monitoring (Live)")
    webrtc_streamer(
        key="emotion-analyzer",
        video_processor_factory=EmotionMonitor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    # Live emotion readout
    if emotion_queue:
        current_emo = emotion_queue[-1]
        st.session_state.last_emotion = current_emo
        st.markdown(f"**Detected Emotion:** `{current_emo['emotion']}` ({current_emo['confidence']:.1f}%)")

    # Suspicious flags
    if flag_queue and flag_queue[-1]:
        for flag in flag_queue[-1]:
            st.warning(flag)

    # Interview questions loop
    if st.session_state.q_index < len(st.session_state.questions):
        idx = st.session_state.q_index
        q = st.session_state.questions[idx]

        st.subheader(f"Question {idx + 1}")
        st.info(q)

        text_answer = st.text_area("✍️ Type your answer:",key=f"text_{idx}",value=st.session_state.get(f"mic_answer_{idx}", ""))

        mic_col, submit_col = st.columns([1, 2])

        with mic_col:
            if st.button("🎙 Use Microphone"):
                mic_answer = record_audio()
                st.session_state[f"mic_answer_{idx}"] = mic_answer
                st.experimental_rerun()

        with submit_col:
            if st.button("✅ Submit Answer"):
                final_answer = st.session_state.get(f"text_{idx}", text_answer)
                with st.spinner("Evaluating your answer..."):
                    feedback = evaluate_answer(q, final_answer)
                    print("Feedback:", feedback)

                    score_line = [line for line in feedback.split("\n") if "score" in line.lower()]
                    score = int(''.join(filter(str.isdigit, score_line[0]))) if score_line else 0

                    st.session_state.feedbacks.append(feedback)
                    st.session_state.scores.append(score)
                    st.session_state.emotions.append(st.session_state.last_emotion.copy())
                    st.session_state.flags.append(flag_queue[-1] if flag_queue else [])
                    st.session_state.q_index += 1
                    st.rerun()

    else:
        # Completion screen
        st.success("✅ Interview Completed!")
        avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
        st.metric("Average Score", f"{avg_score:.1f} / 10")

        for i, (q, fb, emo, score, flags) in enumerate(zip(
            st.session_state.questions,
            st.session_state.feedbacks,
            st.session_state.emotions,
            st.session_state.scores,
            st.session_state.flags
        )):
            with st.expander(f"Q{i+1}: {q}"):
                st.markdown(f"**Score:** `{score}/10`")
                st.markdown(f"**Emotion:** {emo['emotion'].title()} ({emo['confidence']:.1f}%)")
                if flags:
                    st.markdown("**Flags:**")
                    for flag in flags:
                        st.warning(flag)
                st.text(fb)

        # Download feedback
        st.download_button(
            label="📥 Download Feedback",
            data="\n\n".join(st.session_state.feedbacks),
            file_name="interview_feedback.txt",
            mime="text/plain"
        )
