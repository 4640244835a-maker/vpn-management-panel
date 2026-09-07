from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.user import User

router = APIRouter()

@router.get("/{token}")
async def get_subscription(token: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where((User.uuid == token) | (User.username == token)))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        sub_content = f"# Marzban Subscription for {user.username}\nvless://{user.uuid}@example.com:443?security=reality&type=tcp#{user.username}\n"
        return Response(content=sub_content, media_type="text/plain")
