from pydantic import BaseModel
from typing import Optional

class UserLogin(BaseModel):
    username: str

class FaceVerificationRequest(BaseModel):
    user_id: str
    registered_image: str  # base64-encoded
    captured_image: str    # base64-encoded

class FaceVerificationResponse(BaseModel):
    status: str
    confidence: Optional[float]
    message: Optional[str]
