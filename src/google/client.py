import httpx
import urllib.parse
import os
from google.oauth2 import client

class GoogleClient:
  """A Google client class that uses httpx async."""

  def __init__(self):
    self.client_id = os.getenv('GOOGLE_CLIENT_ID')
    self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    self.client  = client.Credentials(
    token_uri='https://oauth2.googleapis.com/token',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
)
  async def _make_request(self, method, url, headers=None, data=None):
    """Makes a request to the Google API.

    Args:
      method: The HTTP method.
      url: The URL.
      headers: The request headers.
      data: The request body.

    Returns:
      The response.
    """

    async with httpx.AsyncClient() as client:
      response = await client.request(
        method,
        url,
        headers=headers,
        data=data,
        timeout=30,
      )

      response.raise_for_status()

      return response

  async def exchange_code_for_tokens(self, code):
    """Exchanges an authorization code for an access token and refresh token.

    Args:
      code: The authorization code.

    Returns:
      A dictionary containing the access token and refresh token.
    """
    
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
      data=payload,
    )

    response.raise_for_status()

    tokens = response.json()

    return tokens

  async def get_consent_url(self, scope):
    """Generates a Google consent URL with the desired scope.

    Args:
      scope: A space-separated list of the scopes that the application requires.

    Returns:
      A Google consent URL.
    """

    query_params = {
      "client_id": self.client_id,
      "response_type": "code",
      "scope": scope,
      "redirect_uri": self.redirect_uri,
    }

    query_string = urllib.parse.urlencode(query_params)

    consent_url = "https://accounts.google.com/o/oauth2/v2/auth?" + query_string

    return consent_url
