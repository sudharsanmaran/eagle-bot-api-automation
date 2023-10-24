import datetime
import json
from fastapi import HTTPException
import httplib2
import httpx
import urllib.parse
import os
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


logger = logging.getLogger(__name__)


class GoogleClient:
    """A Google client class that uses httpx async."""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        self.token_uri = "https://oauth2.googleapis.com/token"

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
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "token_uri": self.token_uri,
            }
        )
        return credentials

    async def get_valid_credential(self, tokens) -> Credentials:
        """Returns a valid Google credential object from tokens."""

        credentials = await self.get_credential(tokens)
        is_refreshed = False
        if credentials.expired:
            credentials.refresh(httplib2.Http())
            is_refreshed = True

        return credentials, is_refreshed

    async def get_user_profile(self, credentials: Credentials) -> dict:
        """Returns the user's profile from Google."""

        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info

    async def send_mail(self, to, subject, body, cc=None, bcc=None):
        """Sends an email to the specified recipient."""
        pass
