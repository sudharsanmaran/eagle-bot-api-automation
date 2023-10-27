import json
from fastapi import HTTPException
import httpx
import urllib.parse
from urllib.parse import urlencode, quote
import os
from src.jira.utils import dict2str

from src.jira.constants import BASE_URL_FOR_JIRA_API, CONTENTTYPE, JIRA_OAUTH_TOKEN_URL


class JiraClient:
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
                    timeout=60,
                )

                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as err:
                details = json.loads(err.response.text)
                raise HTTPException(
                    status_code=err.response.status_code,
                    detail=details,
                )

    async def exchange_code_for_tokens(self, code):
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {"Content-Type": CONTENTTYPE["AXFORM"]}

        response = await self._make_request(
            "POST",
            JIRA_OAUTH_TOKEN_URL,
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

    async def get_consent_url(self, scope: str, err_mess: str):
        query_params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "response_type": "code",
            "scope": scope,
            "state": "qwerty123",
            "prompt": "consent",
            "redirect_uri": self.redirect_uri,
        }
        query_string = urlencode(query_params, quote_via=quote)

        consent_url = f"https://auth.atlassian.com/authorize?" + query_string
        details = {
            "error": err_mess,
            "consent_url": consent_url,
        }
        raise HTTPException(
            status_code=400,
            detail=details,
        )

    async def get_jira_rotational_token(self, refresh_token: str, scopes: str):
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        headers = {"Content-Type": CONTENTTYPE["AJSON"]}
        try:
            response = await self._make_request(
                method="POST",
                url=JIRA_OAUTH_TOKEN_URL,
                headers=headers,
                data=json.dumps(data),
            )
            return response
        except HTTPException as err:
            if err.detail["error"] == "unauthorized_client":
                await self.get_consent_url(dict2str(scopes), "unauthorized_client")
            return response

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

    async def create_project(self, resource: object, jira_user: object, data):
        """Creates a new project in Jira."""
        data["projectTemplateKey"] = "com.pyxis.greenhopper.jira:gh-simplified-basic"
        data["projectTypeKey"] = "software"
        data["leadAccountId"] = jira_user.account_id
        cloudid = resource.resource_id
        headers = {
            "Authorization": f"Bearer {resource.access_token}",
            "Content-Type": "application/json",
        }

        response = await self._make_request(
            "POST",
            BASE_URL_FOR_JIRA_API.format(cloudid) + "rest/api/3/project",
            headers=headers,
            data=json.dumps(data),
        )

        return response

    async def create_issue(self, resource: object, jira_user: object, data):
        """Creates a new issue for project in Jira."""
        payload = {
            "fields": {
                "summary": data['summary'],
                "project": {"id": data['project']},
                "issuetype": {"id": data['issuetype']},
            }
        }
        cloudid = resource.resource_id
        headers = {
            "Authorization": f"Bearer {resource.access_token}",
            "Content-Type": "application/json",
        }

        response = await self._make_request(
            "POST",
            BASE_URL_FOR_JIRA_API.format(cloudid) + "rest/api/3/issue",
            headers=headers,
            data=json.dumps(payload),
        )

        return response
