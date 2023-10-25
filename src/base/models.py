from typing import List
import uuid
from sqlalchemy import UUID, Column, DateTime, func, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from src.base.mixins import TimestampMixin, UUIDMixin

from src.google.models import GoogleToken
from src.database import Base



    
    
class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email: Mapped[str] = Column(String, nullable=False, unique=True, index=True)
    access_token: Mapped[str] = Column(String, nullable=False) # incase need to call any admin server's api
    expires_at: Mapped[int] = Column(Integer, nullable=False)

    google_token: Mapped[List[GoogleToken]] = relationship('GoogleToken', back_populates='user', uselist=True)
