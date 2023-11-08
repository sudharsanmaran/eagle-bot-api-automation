from datetime import datetime
import uuid
from sqlalchemy import BOOLEAN, UUID, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped

from src.database import Base
from src.base.mixins import TimestampMixin, TokenInfoMixin, UUIDMixin


class JiraUser(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "jira_users"

    expires_at: Mapped[datetime] = Column(DateTime, nullable=False)


class JiraResouces(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jira_resouces"

    user_id: Mapped[uuid.UUID] = Column(
        UUID, ForeignKey("jira_users.id"), nullable=False
    )
    resource_id: Mapped[uuid.UUID] = Column(
        UUID, nullable=False, unique=True, index=True
    )
    resource_name: Mapped[str] = Column(String, nullable=False)
    default: Mapped[bool] = Column(BOOLEAN, nullable=False, default=False)
    avatar_url: Mapped[str] = Column(String, nullable=True)
