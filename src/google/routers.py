#  create fastapi router for google
from fastapi import APIRouter, Depends

from .dependencies import token_service
from .schemas import AuthCode
from .client import GoogleClient

google_router = APIRouter(tags=["google"], prefix="/v1/google")

client = GoogleClient()


@google_router.get("/consent_url")
async def google_login() -> str:
    res = await client.get_consent_url(scope="https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email")
    return res


@google_router.post("/auth_code")
async def google_Oauth2_callback(code: AuthCode, token_service = Depends(token_service)) -> str:
    """Google OAuth2 callback endpoint."""

    tokens = await client.exchange_code_for_tokens(code)

    return "success, recieved tokens"