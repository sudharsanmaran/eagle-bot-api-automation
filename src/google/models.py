from src.base.models import TimestampMixin, UUIDMixin, TokenInfoMixin, User
from src.database import Base
from sqlalchemy.orm import Mapped, relationship

class GoogleToken(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "google_tokens"

    user: Mapped[User] = relationship('User', back_populates='google_token')

    def __repr__(self) -> str:
        return f'<GoogleToken {self.email} {self.display_name}>'
