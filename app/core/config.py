from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Marzban-X VPN Panel"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    JWT_SECRET_KEY: str = "marzban_super_secret_jwt_key_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./vpn_panel.db"
    XRAY_GRPC_HOST: str = "127.0.0.1"
    XRAY_GRPC_PORT: int = 10085
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ADMIN_ID: Optional[int] = None
    TELEGRAM_ALERT_THRESHOLD_PERCENT: float = 80.0
    SUBSCRIPTION_BASE_URL: str = "https://your-domain.railway.app"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()