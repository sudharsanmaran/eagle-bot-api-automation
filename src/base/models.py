from typing import List
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Mapped, relationship
from src.base.mixins import TimestampMixin, UUIDMixin

from src.database import Base


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = Column(String, nullable=False, unique=True, index=True)
    access_token: Mapped[str] = Column(
        String, nullable=False
    )  # incase need to call any admin server's api
    expires_at: Mapped[int] = Column(Integer, nullable=False)

