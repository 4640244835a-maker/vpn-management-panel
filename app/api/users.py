import uuid
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users Management"])

class UserCreate(BaseModel):
    username: str
    data_limit_gb: float = 30.0
    expire_days: int = 30
    inbounds: List[str] = ["VLESS Reality TCP", "VMess WS", "Trojan gRPC"]
    note: Optional[str] = ""

USERS_DB = [
    {
        "id": 1,
        "username": "alex_pro",
        "uuid": "4f9d2a3e-b5c6-4e8a-9f0d-1e2a3b4c5d6e",
        "subscription_token": "sub_alex_89234892",
        "subscription_url": "https://fra.node.railway.app/sub/sub_alex_89234892",
        "status": "active",
        "used_traffic_bytes": 28456000000,
        "used_traffic_gb": 26.5,
        "data_limit_bytes": 53687091200,
        "data_limit_gb": 50.0,
        "usage_percent": 53.0,
        "expire_date": "2026-10-15T00:00:00",
        "days_left": 37,
        "created_at": "2026-08-01T12:00:00",
        "inbounds": ["VLESS Reality TCP", "VMess WS", "Trojan gRPC"],
        "note": "Priority VIP user"
    }
]

@router.get("")
async def list_users():
    return USERS_DB

@router.post("")
async def create_user(user_in: UserCreate):
    new_user = {
        "id": len(USERS_DB) + 1,
        "username": user_in.username,
        "uuid": str(uuid.uuid4()),
        "subscription_token": f"sub_{uuid.uuid4().hex[:12]}",
        "subscription_url": f"https://fra.node.railway.app/sub/sub_{uuid.uuid4().hex[:12]}",
        "status": "active",
        "used_traffic_bytes": 0,
        "used_traffic_gb": 0.0,
        "data_limit_bytes": int(user_in.data_limit_gb * 1024**3),
        "data_limit_gb": user_in.data_limit_gb,
        "usage_percent": 0.0,
        "expire_date": "2026-10-15T00:00:00",
        "days_left": user_in.expire_days,
        "created_at": "2026-09-08T00:00:00",
        "inbounds": user_in.inbounds,
        "note": user_in.note
    }
    USERS_DB.append(new_user)
    return new_user
