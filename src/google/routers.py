#  create fastapi router for google
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.auth import JWTBearer
from src.base.schemas import Response, User
from src.base.services import UserService
from .client import GoogleClient
from .constants import ERRORS, SCOPES
from .dependencies import token_service, user_service
from .schemas import AuthCode, GoogleTokenInfo, GoogleTokens, SendMail
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
    consent_url = await client.get_consent_url(scopes=scopes)
    details = {
        "message": ERRORS["MISSING_SCOPES"],
        "consent_url": consent_url,
    }
    raise HTTPException(status_code=400, detail=details)


async def get_tokens(scopes: List, user, service: GoogleTokenService):
    """Gets the access token for the user, or raises an exception"""

    tokens = service.get_access_token(user_id=user.id, default=True)
    if not tokens:
        await raise_no_user_exception(scopes)
    combained_scopes = combine_scopes({*tokens.scopes.keys(), *scopes})
    if not all(scope in tokens.scopes for scope in scopes):
        await raise_missing_scopes_exception(combained_scopes)
    return tokens, combained_scopes


async def get_updated_credential(scopes: str, user: dict, service: GoogleTokenService):
    global client
    tokens, combained_scopes = await get_tokens(
        scopes=scopes, user=user, service=service
    )
    credential, is_refreshed = await client.get_valid_credential(
        tokens, combained_scopes
    )
    if is_refreshed:
        tokens.access_token = credential.token
        tokens.refresh_token = credential.refresh_token
        tokens.expires_at = credential.expiry
        service.update(tokens)
    return credential, tokens.email, combained_scopes


def get_user(user_info, service: UserService):
    return service.get_by_email(email=user_info["email"])


def get_expires_at_datetime(google_tokens):
    return (
        datetime.datetime.utcnow()
        + datetime.timedelta(seconds=google_tokens["expires_in"])
        - datetime.timedelta(seconds=60)
    )


async def get_updated_credential_with_scopes(
    user_info, token_service, user_service, scopes
):
    user = get_user(user_info, user_service)
    if not user:
        await raise_no_user_exception(scopes)

    credentials, email, combained_scopes = await get_updated_credential(
        scopes=scopes, user=user, service=token_service
    )
    return credentials, email, combained_scopes


@google_router.post("/oauth_callback")
async def google_Oauth2_callback(
    data: AuthCode,
    token_data=Depends(JWTBearer()),
    token_service: GoogleTokenService = Depends(token_service),
    user_service: UserService = Depends(user_service),
) -> Response:
    """Google OAuth2 callback endpoint."""

    global client
    google_tokens = await client.exchange_code_for_tokens(data.code)
    expires_at = get_expires_at_datetime(google_tokens)
    credential = await client.get_credential(
        GoogleTokens(**google_tokens, expires_at=expires_at)
    )
    profile = await client.get_user_profile(credentials=credential)
    user_info, sso_token = token_data
    user_data = User(
        email=user_info["email"], access_token=sso_token, expires_at=user_info["exp"]
    )
    user = user_service.create_or_update(user_data.model_dump(), lookup_field="email")
    scopes_list = google_tokens["scope"].split()
    scopes_dict = dict.fromkeys(scopes_list, True)
    google_token_data = GoogleTokenInfo(
        user_id=user.id,
        email=profile["email"],
        account_id=profile["id"],
        display_name=profile["name"],
        access_token=google_tokens["access_token"],
        refresh_token=google_tokens["refresh_token"],
        default=True,
        scopes=scopes_dict,
        expires_at=expires_at,
        extra_info={"id_token": google_tokens["id_token"]},
    )
    token_service.unset_default_and_create_or_update(google_token_data.model_dump())
    return {
        "status_code": 200,
        "detail": {
            "message": "Google authentication successful.",
        },
    }


@google_router.get("/all_avaialble_accounts")
async def get_all_available_accounts(
    token_data=Depends(JWTBearer()),
    token_service: GoogleTokenService = Depends(token_service),
    user_service: UserService = Depends(user_service),
) -> Response:
    """Gets all available accounts for the user."""

    user_info, _ = token_data
    user = get_user(user_info, user_service)
    if not user:
        await raise_no_user_exception(SCOPES["BASIC"])

    accounts = token_service.get_all(user_id=user.id)
    emails = [account.email for account in accounts]

    return {
        "status_code": 200,
        "detail": {
            "message": "Accounts fetched successfully.",
            "data": {"accounts": emails},
        },
    }


@google_router.post("/send_email")
async def send_email(
    data: SendMail,
    token_data=Depends(JWTBearer()),
    token_service: GoogleTokenService = Depends(token_service),
    user_service: UserService = Depends(user_service),
) -> Response:
    """Sends an email to the specified recipient."""

    global client
    scopes = [*SCOPES["BASIC"], *SCOPES["SEND_EMAIL"]]
    user_info, _ = token_data
    credentials, email, combained_scopes = await get_updated_credential_with_scopes(
        user_info, token_service, user_service, scopes
    )
    response = await client.send_mail(
        **data.model_dump(),
        from_email=email,
        credentials=credentials,
        combained_scopes=combained_scopes
    )
    return {
        "status_code": 200,
        "detail": {
            "message": "Email sent successfully.",
            "data": response,
        },
    }
