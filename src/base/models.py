from typing import List
import uuid
from sqlalchemy import UUID, Column, DateTime, func, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from src.database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(),
                        onupdate=func.current_timestamp())


class UUIDMixin:
    id: Mapped[uuid.UUID] = Column(UUID, primary_key=True, default=lambda: uuid.uuid4())
    

class TokenInfoMixin:
    user_id: Mapped[uuid.UUID] = Column(UUID, ForeignKey('users.id'), nullable=False)
    email: Mapped[str] = Column(String, nullable=False)
    account_id: Mapped[str] = Column(String, nullable=False)
    display_name: Mapped[str] = Column(String, nullable=False)
    access_token: Mapped[str] = Column(String, nullable=False)
    refresh_token: Mapped[str] = Column(String, nullable=False)
    expires_at: Mapped[int] = Column(Integer, nullable=False)
    extra_info: Mapped[JSON]  = Column(JSON, nullable=True)
    
    
class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email: Mapped[str] = Column(String, nullable=False, unique=True)
    access_token: Mapped[str] = Column(String, nullable=False) # incase need to call any admin server's api
    expires_at: Mapped[int] = Column(Integer, nullable=False)

    google_token: Mapped[List[TokenInfoMixin]] = relationship('GoogleToken', back_populates='user', uselist=True)
