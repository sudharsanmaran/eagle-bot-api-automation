from src.base.models import TimestampMixin, UUIDMixin, TokenInfoMixin
from src.database import Base
from sqlalchemy import Column, JSON, String, Integer
from sqlalchemy.orm import Mapped

class MicrosoftToken(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "microsoft_tokens"
