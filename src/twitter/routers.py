from fastapi import APIRouter
from .client import TwitterClient

twitter_router = APIRouter(tags=["twitter"], prefix="/v1/twitter")

client = TwitterClient()


@twitter_router.get("/consent_url")
def twitter_login() -> str:
    """Generates a Twitter consent URL."""

    res =  client.get_authorize_url(
        scopes="tweet.read tweet.write users.read offline.access"
    )

    return res


@twitter_router.post("/auth_code")
def twitter_Oauth2_callback(code: str) -> str:
    """Twitter OAuth2 callback endpoint."""

    tokens =  client.get_token(code)
    print(tokens)

    return "success, recieved tokens"
