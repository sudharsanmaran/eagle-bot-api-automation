import uuid
from sqlalchemy import DateTime, UUID, Column, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped

from src.database import Base
from src.base.mixins import TimestampMixin, UUIDMixin
from src.base.models import User

class JiraUser(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jira_users"

    user_id: Mapped[uuid.UUID] = Column(UUID, ForeignKey('users.id'), nullable=False)
    email: Mapped[str] = Column(String, nullable=False, unique=True, index=True)
    account_id: Mapped[str] = Column(String, nullable=False)
    display_name: Mapped[str] = Column(String, nullable=False)

class JiraResouces(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jira_resouces"
    
    user_id: Mapped[uuid.UUID] = Column(UUID, ForeignKey('jira_users.id'), nullable=False)
    resource_id: Mapped[uuid.UUID] = Column(UUID, nullable=False, unique=True, index=True)
    resource_name: Mapped[str] = Column(String, nullable=False)
    access_token: Mapped[str] = Column(String, nullable=False)
    refresh_token: Mapped[str] = Column(String, nullable=False)
    scopes: Mapped[JSON] = Column(JSON, nullable=False)
    expires_at: Mapped[DateTime] = Column(DateTime, nullable=False)