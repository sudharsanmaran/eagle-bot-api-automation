#  create fastapi router for google
from fastapi import APIRouter, Depends

from src.auth import JWTBearer

from .client import GoogleClient
from .constants import SCOPE
from .dependencies import token_service, get_access_token
from .schemas import AuthCode, SendMail
from .services import GoogleTokenService

google_router = APIRouter(tags=["google"], prefix="/v1/google")

client = GoogleClient()


@google_router.get("/consent_url")
async def google_login() -> str:
    res = await client.get_consent_url(
        scope="https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    )
    return res


@google_router.post("/auth_code")
async def google_Oauth2_callback(
    code: AuthCode, token_service=Depends(token_service),
    user = Depends(JWTBearer())
) -> str:
    """Google OAuth2 callback endpoint."""

    tokens = await client.exchange_code_for_tokens(code)

    return "success, recieved tokens"


@google_router.post("/send_email")
async def send_email(
    data: SendMail,
    user = Depends(JWTBearer()),
    token_service: GoogleTokenService =Depends(token_service),
    access_token = Depends(get_access_token(scope=SCOPE["SEND_EMAIL"])),
) -> str:
    """Sends an email to the specified recipient."""

    await client.send_mail(**data.model_dump())

    return "success, email sent"