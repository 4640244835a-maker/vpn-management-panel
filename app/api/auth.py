from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/token", response_model=TokenResponse)
async def login(req: AdminLoginRequest):
    if req.username == settings.ADMIN_USERNAME and req.password == settings.ADMIN_PASSWORD:
        return TokenResponse(access_token="authenticated-admin-session-token")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="نام کاربری یا رمز عبور اشتباه است"
    )
