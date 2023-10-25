# schemas

import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from src.base.schemas import TokenInfo


class AuthCode(BaseModel):
    code: str = Field(
        ...,
        example="4/0AY0e-g7G4rH1c4Jz4d2X2Y5o6d7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f6g7h8i9j0k",
    )


class SendMail(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None


class GoogleTokens(BaseModel):
    access_token: str
    expires_at: datetime.datetime
    refresh_token: str
    scope: str
    token_type: str
    id_token: str


class GoogleTokenInfo(TokenInfo):
    expires_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)
