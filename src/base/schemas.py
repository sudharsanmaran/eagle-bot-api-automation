from typing import Dict, Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    email: EmailStr
    access_token: str
    expires_at: int
    model_config = ConfigDict(from_attributes=True)


class TokenInfo(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    account_id: str
    display_name: str
    access_token: str
    refresh_token: str
    scopes: Dict
    expires_at: int
    extra_info: Optional[Dict]


class Detail(BaseModel):
    message: str
    data: Optional[Dict] = None
    error: Optional[Dict] = None


class Response(BaseModel):
    status_code: int
    detail: Detail
