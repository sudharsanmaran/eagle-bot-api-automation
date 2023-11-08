import uuid
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    func,
    String,
    Integer,
    JSON,
    ForeignKey,
    BOOLEAN,
)
from sqlalchemy.orm import Mapped


class TimestampMixin:
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = Column(UUID, primary_key=True, default=lambda: uuid.uuid4())


class TokenInfoMixin:
    user_id: Mapped[uuid.UUID] = Column(UUID, ForeignKey("users.id"), nullable=False)
    email: Mapped[str] = Column(String, nullable=False, unique=True, index=True)
    account_id: Mapped[str] = Column(String, nullable=True)
    display_name: Mapped[str] = Column(String, nullable=False)
    access_token: Mapped[str] = Column(String, nullable=False)
    refresh_token: Mapped[str] = Column(String, nullable=False)
    scopes: Mapped[JSON] = Column(JSON, nullable=False)
    default: Mapped[bool] = Column(BOOLEAN, nullable=False, default=False)
    expires_at: Mapped[int] = Column(Integer, nullable=False)
    extra_info: Mapped[JSON] = Column(JSON, nullable=True)
