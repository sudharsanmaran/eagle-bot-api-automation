import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import Mapped, relationship

from src.base.mixins import TimestampMixin, UUIDMixin, TokenInfoMixin
from src.database import Base
from src.base.models import User


class GoogleToken(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "google_tokens"

    expires_at: Mapped[datetime.datetime] = Column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<GoogleToken {self.email} {self.display_name}>"
