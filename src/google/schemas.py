# schemas

from pydantic import BaseModel, Field


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
