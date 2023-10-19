#  create fastapi router for google
from fastapi import APIRouter
from .client import GoogleClient

google_router = APIRouter(tags=["google"], prefix="/google")

client = GoogleClient()


@google_router.get("/consent_url")
async def google_login() -> str:
    res = await client.get_consent_url(scope="https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email")
    return res


@google_router.get("/callback")
async def google_callback(code: str):
    res = await client.exchange_code_for_tokens(code)
    return res