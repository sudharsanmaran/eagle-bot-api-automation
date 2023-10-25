from fastapi import HTTPException
import httpx
import urllib.parse
import os

from src.jira.constants import BASE_URL_FOR_JIRA_API


class JiraClient:
    """A jira client class that uses httpx async."""

    def __init__(self):
        self.client_id = os.getenv("jira_CLIENT_ID")
        self.client_secret = os.getenv("jira_CLIENT_SECRET")
        self.redirect_uri = os.getenv("jira_REDIRECT_URI")

    async def _make_request(self, method, url, headers=None, data=None):
        """Makes a request to the jira API.

        Args:
          method: The HTTP method.
          url: The URL.
          headers: The request headers.
          data: The request body.

        Returns:
          The response.
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    data=data,
                    timeout=30,
                )

                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code, detail=str(exc)
                )
            return response.json()

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
            "https://auth.atlassian.com/oauth/token",
            headers=headers,
            data=urllib.parse.urlencode(payload),
        )

        return response
    
    async def get_Jira_user(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._make_request(
            "GET",
            "https://api.atlassian.com/me",
            headers=headers,
        )
        
        return response
    
    async def get_user_accessible_resources(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._make_request(
            "GET",
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers=headers,
        )
        return response

    async def get_consent_url(self, scope: str):
        """Generates a jira consent URL with the desired scope.

        Returns:
          A jira consent URL.
        """

        query_params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "response_type": "code",
            "scope": scope,
            "state": "qwerty123",
            "prompt": "consent",
            "redirect_uri": self.redirect_uri,
        }

        query_string = urllib.parse.urlencode(query_params)

        consent_url = f"https://auth.atlassian.com/authorize?" + query_string

        return consent_url

    def fetch_jira_details_for_user(self, user_eamil):
        # later get access token for user eamil
        res = {
            "access_token": os.getenv("JIRA_ACCESS_TOKEN"),
            "account_id": "712020:aaa48bf2-83ff-4e44-835e-70f8abe0047a",
            "resources_details": {
                "id": "cd1ede5c-127f-4405-a54a-05ff6578a764",
                "url": "https://eaglebottest2.atlassian.net",
                "name": "eaglebottest2",
                "scopes": [],
                "avatarUrl": "https://site-admin-avatar-cdn.prod.public.atl-paas.net/avatars/240/koala.png",
            },
        }

        return res

    async def create_project(self, user_eamil, data):
        """Creates a new project in Jira."""
        user_jira_details = self.fetch_jira_details_for_user(user_eamil)
        data["leadAccountId"] = user_jira_details["account_id"]
        cloudid = user_jira_details["resource_details"].get("id")
        headers = {"Authorization": f"Bearer {user_jira_details['access_token']}"}

        response = await self._make_request(
            "POST",
            f"{BASE_URL_FOR_JIRA_API}rest/api/3/project".format(cloudid),
            headers=headers,
            data=data,
        )

        return response
