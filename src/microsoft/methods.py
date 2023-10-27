import os


def get_busy_or_free_schedule_scopes():
    return [
        'Calendars.Read.Shared',
        'Calendars.Read',
        'offline_access'
    ]


def generate_json_for_microsoft_code(scopes):
    return {
        'client_id': os.environ.get('MICROSOFT_CLIENT_ID'),
        'redirect_uri': os.environ.get('MICROSOFT_REDIRECT_URL'),
        'response_type': 'code',
        'scope': ' '.join(scopes),
    }


def generate_json_for_token(code: str):
    return {
        'code': code,
        'client_id': os.environ.get('MICROSOFT_CLIENT_ID'),
        'client_secret': os.environ.get('MICROSOFT_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('MICROSOFT_REDIRECT_URL'),
        'grant_type': 'authorization_code',
    }


def generate_json_for_refresh_token(refresh_token: str):
    return {
        'refresh_token': refresh_token,
        'client_id': os.environ.get('MICROSOFT_CLIENT_ID'),
        'client_secret': os.environ.get('MICROSOFT_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('MICROSOFT_REDIRECT_URL'),
        'grant_type': 'refresh_token',
    }
