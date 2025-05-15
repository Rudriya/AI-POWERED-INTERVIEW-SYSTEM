import base64
import requests

def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")

def send_verification_request(user_id, registered_b64, captured_b64, api_url):
    payload = {
        "user_id": user_id,
        "registered_image": registered_b64,
        "captured_image": captured_b64
    }
    try:
        res = requests.post(f"{api_url}/verify_face/", json=payload, timeout=30)
        return res.json() if res.status_code == 200 else {"status": "error", "message": res.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
