from enum import Enum


class AvailableScopes(Enum):
    BASIC = "BASIC"
    SEND_EMAIL = "SEND_EMAIL"


SCOPES = {
    "BASIC": ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
    "SEND_EMAIL": ["https://www.googleapis.com/auth/gmail.send"],
}


ERRORS = {
    "NO_USER": """User not found. Please provide consent, then call the auth_code endpoint with the authorization code and try again.""",
    "MISSING_SCOPES": """User has not provided consent for the required scopes. Please provide consent, then call the auth_code endpoint with the authorization code and try again.""",
}
