import os, base64, cv2
import numpy as np
from deepface import DeepFace

def decode_image(b64_string):
    return cv2.imdecode(np.frombuffer(base64.b64decode(b64_string), np.uint8), cv2.IMREAD_COLOR)

def verify_faces(user_id, registered_b64, captured_b64):
    try:
        user_folder = f"user_data/{user_id}"
        os.makedirs(user_folder, exist_ok=True)
        reg_path = os.path.join(user_folder, "registered.jpg")
        cap_path = os.path.join(user_folder, "captured.jpg")

        reg_img = decode_image(registered_b64)
        cap_img = decode_image(captured_b64)

        cv2.imwrite(reg_path, reg_img)
        cv2.imwrite(cap_path, cap_img)

        result = DeepFace.verify(img1_path=reg_path, img2_path=cap_path, model_name="VGG-Face")
        return {
            "status": "verified" if result["verified"] else "not_verified",
            "confidence": 1 - result["distance"],
            "message": "Match success" if result["verified"] else "Face mismatch",
            "success": True
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
