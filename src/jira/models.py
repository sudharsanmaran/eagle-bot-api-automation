from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from src.database import Base
from src.base.models import TimestampMixin, UUIDMixin, TokenInfoMixin


"""
example get user response from jira api
{
        "self": "https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g",
        "key": "",
        "accountId": "5b10a2844c20165700ede21g",
        "accountType": "atlassian",
        "name": "",
        "emailAddress": "mia@example.com",
        "avatarUrls": {
            "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=48&s=48",
            "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=24&s=24",
            "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=16&s=16",
            "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=32&s=32",
        },
        "displayName": "Mia Krystof",
        "active": true,
        "timeZone": "Australia/Sydney",
        "groups": {"size": 3, "items": []},
        "applicationRoles": {"size": 1, "items": []},
}"""


class JiraToken(Base, UUIDMixin, TokenInfoMixin, TimestampMixin):
    __tablename__ = "jira_tokens"

    domain_name: Mapped[str] = Column(String, nullable=False)
    time_Zone: Mapped[str] = Column(String, nullable=True)

