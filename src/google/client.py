import base64
from email.message import EmailMessage
import json
from typing import List, Optional
from fastapi import HTTPException
from google.auth.transport.requests import Request
import httpx
import urllib.parse
import os
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import Error


logger = logging.getLogger(__name__)


class GoogleClient:
    """A Google client class that uses httpx async."""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.request = Request()

    async def _make_request(self, method, url, headers=None, data=None):
        """Makes a request to the specified URL."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    data=data,
                    timeout=30,
                )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as err:
            logger.error(f"HTTP error occurred: {err}")
            raise HTTPException(
                status_code=err.response.status_code,
                detail=json.loads(err.response.text),
            )

    async def exchange_code_for_tokens(self, code):
        """Exchanges an authorization code for an access token and refresh token."""

        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await self._make_request(
            "POST",
            self.token_uri,
            headers=headers,
            data=urllib.parse.urlencode(payload),
        )

        return response

    async def get_consent_url(self, scopes):
        """Generates a Google consent URL with the desired scope."""

        query_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": scopes,
            "redirect_uri": self.redirect_uri,
            "access_type": "offline",
        }

        query_string = urllib.parse.urlencode(query_params)

        consent_url = "https://accounts.google.com/o/oauth2/v2/auth?" + query_string

        return consent_url

    async def get_credential(self, tokens) -> Credentials:
        """Returns a Google credential object from tokens."""

        credentials = Credentials.from_authorized_user_info(
            {
                "access_token": getattr(tokens, "access_token"),
                "refresh_token": getattr(tokens, "refresh_token"),
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "token_uri": self.token_uri,
                "expiry": getattr(tokens, "expires_at").strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )
        return credentials

    async def get_valid_credential(self, tokens, combained_scopes) -> Credentials:
        """Returns a valid Google credential object from tokens."""

        credentials = await self.get_credential(tokens)
        is_refreshed = False
        if credentials.expired:
            try:
                credentials.refresh(self.request)
                is_refreshed = True
            except Error as error:
                logger.error(f"An error occurred: {error}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "An error occurred while refreshing the token. give consent and try again.",
                        "error": f"{error}",
                        "consent_url": await self.get_consent_url(
                            scopes=combained_scopes
                        ),
                    },
                )

        return credentials, is_refreshed

    async def get_user_profile(self, credentials: Credentials) -> dict:
        """Returns the user's profile from Google."""

        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info

    async def send_mail(
        self,
        to: List,
        subject,
        body,
        credentials: Credentials,
        from_email,
        cc: Optional[List] = None,
        bcc: Optional[List] = None,
        combained_scopes: str = None,
    ):
        """Sends an email to the specified recipient."""
        try:
            service = build("gmail", "v1", credentials=credentials)
            message = EmailMessage()

            message.set_content(body)

            message["To"] = to
            message["From"] = from_email
            message["Subject"] = subject
            if cc:
                message["Cc"] = cc
            if bcc:
                message["Bcc"] = bcc

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            # pylint: disable=E1101
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            logger.info(f'Message Id: {send_message["id"]}')
            return send_message
        except Error as error:
            status_code = error.resp.status
            reason = error._get_reason()

            if status_code == 401 or reason == "invalidCredentials":
                logger.error(f"An error occurred: {error}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "An error occurred while sending the email. give consent and try again.",
                        "error": f"{error}",
                        "consent_url": await self.get_consent_url(
                            scopes=combained_scopes
                        ),
                    },
                )

            logger.error(f"An error occurred: {error}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "An error occurred while sending the email.",
                    "error": reason,
                },
            )
