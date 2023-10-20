from fastapi import HTTPException
import httpx
import urllib.parse
import os
import logging


logger = logging.getLogger(__name__)


class GoogleClient:
    """A Google client class that uses httpx async."""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

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
                status_code=err.response.status_code, detail=err.response.text
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
            "https://oauth2.googleapis.com/token",
            headers=headers,
            data=urllib.parse.urlencode(payload),
        )

        return response

    async def get_consent_url(self, scope):
        """Generates a Google consent URL with the desired scope."""

        query_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": scope,
            "redirect_uri": self.redirect_uri,
            "access_type": "offline",
        }

        query_string = urllib.parse.urlencode(query_params)

        consent_url = "https://accounts.google.com/o/oauth2/v2/auth?" + query_string

        return consent_url
