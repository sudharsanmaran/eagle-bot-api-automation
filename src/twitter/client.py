import os
import tweepy
import httpx
import urllib.parse
import base64


class TwitterClient:
    def __init__(self):
        self.client_id = os.getenv("TWITTER_CLIENT_ID")
        self.client_secret = os.getenv("TWITTER_CLIENT_SECRET")
        self.redirect_uri = os.getenv("TWITTER_REDIRECT_URI")

    def get_consent_url(self, scopes):
        """Generates an authorization URL for the specified scopes."""

        self.auth = tweepy.OAuth2UserHandler(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=scopes,
        )

        return self.auth.get_authorization_url()

    def exchange_code_for_tokens(self, url, scope=None):
        """Exchanges an authorization code for an access token."""

        return self.auth.fetch_token(url)

    def get_client(self, access_token):
        """Creates a Twitter API client using the specified access token."""

        return tweepy.Client(access_token=access_token)
    

    

    def get_token(self, code, code_verifier='test'):
        """Gets an access token using an authorization code."""

        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'code_verifier': code_verifier
        }


        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {os.getenv("TWITTER_CLIENT_ACCESS_TOKEN")}'
        }

        response = httpx.post('https://api.twitter.com/2/oauth2/token', data=data, headers=headers)

        response.raise_for_status()

        return response.json()
    

    def get_authorize_url(self, scopes, state='test', code_challenge='test'):
        """Generates the authorization URL with PKCE."""

        base_url = "https://twitter.com/i/oauth2/authorize"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scopes,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "plain"
        }
        return base_url + "?" + urllib.parse.urlencode(params)
