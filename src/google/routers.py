#  create fastapi router for google
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from src.auth import JWTBearer, decodeJWT
from src.base.schemas import User
from src.base.services import UserService
from .client import GoogleClient
from .constants import ERRORS, SCOPES
from .dependencies import token_service, user_service
from .schemas import AuthCode, GoogleTokenInfo, SendMail
from .services import GoogleTokenService


google_router = APIRouter(tags=["google"], prefix="/v1/google")

client = GoogleClient()


def combine_scopes(scopes: List[str]) -> str:
    """Combines a list of scopes into a single space-separated string."""
    return " ".join(scopes)


async def raise_no_user_exception(scopes):
    scopes = combine_scopes(scopes)
    consent_url = await client.get_consent_url(scopes=scopes)
    details = {
        "message": ERRORS["NO_USER"],
        "consent_url": consent_url,
    }
    raise HTTPException(status_code=400, detail=details)


async def raise_missing_scopes_exception(scopes):
    scopes = combine_scopes(scopes)
    consent_url = await client.get_consent_url(scopes=scopes)
    details = {
        "message": ERRORS["MISSING_SCOPES"],
        "consent_url": consent_url,
    }
    raise HTTPException(status_code=400, detail=details)


async def get_tokens(scopes: str, user: dict, service: GoogleTokenService):
    """Gets the access token for the user, or raises an exception"""

    tokens = service.get_access_token(user_id=user["id"], email=user["email"])
    if not tokens or all(scope in tokens["scopes"] for scope in scopes):
        await raise_missing_scopes_exception(scopes)
    return tokens


async def get_updated_credential(scopes: str, user: dict, service: GoogleTokenService):
    global client
    tokens = await get_tokens(scopes=scopes, user=user, service=token_service)
    credential, is_refreshed = client.get_valid_credential(tokens)
    if is_refreshed:
        service.update(**credential.to_json())
    return credential


def get_user(token, service: UserService):
    return service.get_by_email(token["email"])


async def get_updated_credential_with_scopes(
    token, token_service, user_service, scopes
):
    user = get_user(token, user_service)
    if not user:
        await raise_no_user_exception(scopes)

    credentials = get_updated_credential(
        scopes=scopes, user=user, service=token_service
    )
    return credentials


@google_router.post("/auth_code")
async def google_Oauth2_callback(
    data: AuthCode,
    token_data=Depends(JWTBearer()),
    token_service: GoogleTokenService = Depends(token_service),
    user_service: UserService = Depends(user_service),
) -> str:
    """Google OAuth2 callback endpoint."""

    global client
    # google_tokens = await client.exchange_code_for_tokens(data.code)
    google_tokens = {
        "access_token": "ya29.a0AfB_byAexjs-TivgAaKC3HqeTGKtoPY8kyfBFTTtIFnS9IQyErspI3YvRldSDWT_rvCxzere0OiSvazX_Vs7QOQ5xfvzA1bJa6GL_50qn-TVMCCszy09gDaMbO0ENjO-B3K1UgYJHm0rdNpaDdTkaMvg_VC0muxXKvBWaCgYKAf4SARASFQGOcNnCHLTBBUFC7-TznT1sWSN-xA0171",
        "expires_in": 3599,
        "refresh_token": "1//0gesTNmNWi_31CgYIARAAGBASNwF-L9IrqM2kFcUa140dAoL61D3N40_WSvQcuuKyITkAWlVvZVscSkbNkOIt2MXwVdQ3vKYvp18",
        "scope": "https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/userinfo.email openid https://www.googleapis.com/auth/userinfo.profile",
        "token_type": "Bearer",
        "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImEwNmFmMGI2OGEyMTE5ZDY5MmNhYzRhYmY0MTVmZjM3ODgxMzZmNjUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0NTE3OTkzMjE1NjQtczlrMWhrbWVsaDhjOXA3NHJmamZ2cDg2N2gzaTVnNGUuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0NTE3OTkzMjE1NjQtczlrMWhrbWVsaDhjOXA3NHJmamZ2cDg2N2gzaTVnNGUuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDg4MTYyMjA3MDY4MDQyNzE0MjkiLCJoZCI6InNvZnRzdWF2ZS5jb20iLCJlbWFpbCI6InN1ZGhhcnNhbi5tYXJhcHBhbkBzb2Z0c3VhdmUuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJUX0ZDQU8tQzNvRXlheHRVbVBXUFVBIiwibmFtZSI6IlN1ZGhhcnNhbiBNYXJhcHBhbiIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKSDBZT2Zwc05HX3AxWFFOZGViTFJDdk1DX0U5NG5yZExsdVRyRDFXS0RSUT1zOTYtYyIsImdpdmVuX25hbWUiOiJTdWRoYXJzYW4iLCJmYW1pbHlfbmFtZSI6Ik1hcmFwcGFuIiwibG9jYWxlIjoiZW4iLCJpYXQiOjE2OTgxNTM1NzIsImV4cCI6MTY5ODE1NzE3Mn0.AZI_EyuDG3_HxWEX6jNmwm4dH3KmG_msD8PLyCmhLXnSorqhMtv9sIRlbEV7cypG3l-ZE6uAT9SDhcRA0sEmU7akwADsDppSYMFkwJ9wKN9NtOup7CEd4B-n7yG7VpcfhqSQ9cZVwStAOuvhFO5D2lrngt0IugtqQxtdTX99WI4b-D1xr8Q16g5yNkGsVAyfKNlZY0fvVcQbI6951bPveZpASF1UNRtz461lOTF1nRxj90ErLV5ltqM_QMQyNhlbft5JsAEEofMJXMTGqgLwMAAQjfS7E3b_KQPZWyrRlTigschRgB7chX_hgezLMPcYf7jBEgm-Eljl63qGdcSzdQ",
    }
    credential = await client.get_credential(google_tokens)
    profile = await client.get_user_profile(credentials=credential)
    user_info, sso_token = token_data
    user_data = User(
        email=user_info["email"], access_token=sso_token, expires_at=user_info["exp"]
    )
    user = user_service.create_or_update(user_data.model_dump())
    scopes_list = google_tokens["scope"].split()
    scopes_dict = dict.fromkeys(scopes_list, True)
    google_token_data = GoogleTokenInfo(
        user_id=user.id,
        email=profile["email"],
        account_id=profile["id"],
        display_name=profile["name"],
        access_token=google_tokens["access_token"],
        refresh_token=google_tokens["refresh_token"],
        scopes=scopes_dict,
        expires_at=google_tokens["expires_in"],
        extra_info={"id_token": google_tokens["id_token"]},
    )
    token_service.create_or_update(google_token_data.model_dump(), lookup_field="email")
    return "success, recieved tokens"


@google_router.post("/send_email")
async def send_email(
    data: SendMail,
    token=Depends(JWTBearer()),
    token_service: GoogleTokenService = Depends(token_service),
    user_service: UserService = Depends(user_service),
) -> str:
    """Sends an email to the specified recipient."""

    global client
    scopes = [*SCOPES["BASIC"], *SCOPES["SEND_EMAIL"]]
    credentials = await get_updated_credential_with_scopes(
        token, token_service, user_service, scopes
    )
    res = await client.send_mail(**data.model_dump(), credentials=credentials)
    return "success, email sent"
