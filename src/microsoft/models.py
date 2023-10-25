from sqlalchemy.orm import relationship

from src.base.mixins import TokenInfoMixin, TimestampMixin, UUIDMixin
from src.database import Base


class MicrosoftToken(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "microsoft_tokens"
    user = relationship("User", back_populates="microsoft_tokens")

    def __repr__(self) -> str:
        return f"<MicrosoftToken {self.email} {self.display_name}>"
