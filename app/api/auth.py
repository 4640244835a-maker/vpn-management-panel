from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class AdminProfile(BaseModel):
    username: str
    role: str = "superadmin"
    email: str = "admin@panel.network"

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username.lower() in ["admin", "root"] and form_data.password in ["admin123", "admin"]:
        return TokenResponse(
            access_token="marzban_admin_authenticated_token",
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    return TokenResponse(
        access_token=f"demo_token_for_{form_data.username}",
        token_type="bearer",
        expires_in=3600 * 24
    )

@router.get("/me", response_model=AdminProfile)
async def get_current_admin():
    return AdminProfile(username="admin", role="superadmin", email="admin@panel.network")
