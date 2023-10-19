from src.base.models import TimestampMixin, UUIDMixin, TokenInfoMixin
from src.database import Base

class GoogleToken(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "google_tokens"
