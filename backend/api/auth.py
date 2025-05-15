from fastapi import APIRouter
from models.schemas import UserLogin

router = APIRouter()

@router.post("/login/")
def login_user(user: UserLogin):
    return {"status": "success", "user_id": user.username}
