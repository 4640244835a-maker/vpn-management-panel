import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    LIMITED = "limited"
    EXPIRED = "expired"
    DISABLED = "disabled"

class Inbound(Base):
    __tablename__ = "inbounds"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(64), unique=True, index=True, nullable=False)
    protocol = Column(String(32), default="vless")
    port = Column(Integer, nullable=False)
    tls = Column(String(32), default="none")
    network = Column(String(32), default="tcp")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    user = relationship("User", back_populates="inbounds")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    uuid = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    used_traffic = Column(BigInteger, default=0, nullable=False)
    data_limit = Column(BigInteger, nullable=True)
    expire_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String(255), nullable=True)
    
    inbounds = relationship("Inbound", back_populates="user", cascade="all, delete-orphan")
