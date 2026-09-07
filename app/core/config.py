import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Marzban Xray VPN Manager"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "marzban-secret-key-change-in-production-12345678")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./xray_manager.db")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", None)
    TELEGRAM_ADMIN_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_ADMIN_CHAT_ID", None)
    
    # Xray gRPC
    XRAY_GRPC_HOST: str = os.getenv("XRAY_GRPC_HOST", "127.0.0.1")
    XRAY_GRPC_PORT: int = int(os.getenv("XRAY_GRPC_PORT", "10085"))
    
    # Admin Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
