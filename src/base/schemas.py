

from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    email: EmailStr
    access_token: str
    expires_at: int
    model_config = ConfigDict(from_attributes=True)
