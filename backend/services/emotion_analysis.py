from deepface import DeepFace
import numpy as np

def analyze_emotion(frame: np.ndarray):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant = result[0]['dominant_emotion']
        confidence = result[0]['emotion'][dominant]
        return {
            "emotion": dominant,
            "confidence": confidence
        }
    except Exception as e:
        return {
            "emotion": "unknown",
            "confidence": 0.0,
            "error": str(e)
        }
