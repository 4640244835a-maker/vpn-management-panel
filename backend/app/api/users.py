from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    username: str
    uuid: str
    status: str
    used_traffic: int
    data_limit: Optional[int]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
