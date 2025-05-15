from fastapi import APIRouter, HTTPException
from models.schemas import FaceVerificationRequest, FaceVerificationResponse
from services.face_verification import verify_faces

router = APIRouter()

@router.post("/verify_face/", response_model=FaceVerificationResponse)
def face_verify(request: FaceVerificationRequest):
    result = verify_faces(request.user_id, request.registered_image, request.captured_image)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return FaceVerificationResponse(**result)
