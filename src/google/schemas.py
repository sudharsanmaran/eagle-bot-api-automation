# schemas

from typing import List, Optional, Dict
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, Json


class AuthCode(BaseModel):
    code: str = Field(
        ...,
        example="4/0AY0e-g7G4rH1c4Jz4d2X2Y5o6d7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f6g7h8i9j0k",
    )


class SendMail(BaseModel):
    to: str
    subject: str
    body: str
    cc: str
    bcc: str
    

class GoogleTokenInfo(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    account_id: str
    display_name: str
    access_token: str
    refresh_token: str
    scopes: Dict
    expires_at: int
    extra_info: Optional[Dict]
    model_config = ConfigDict(from_attributes=True)
