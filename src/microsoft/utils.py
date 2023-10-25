from datetime import datetime
import os

import requests

from src.auth import JWTBearer
from src.base.decorators import Authorization
from src.microsoft.methods import generate_json_for_microsoft_code, generate_json_for_token
from src.base.services import ListCreateUpdateRetriveDeleteService, UserService
from src.base.utils import Platform
from typing import List, Type

from requests import PreparedRequest

from src.microsoft import InitialMicrosoftGraphURLs
from src.microsoft.client import UserAPI


@Authorization
def get_access_token_or_url(platform: str, scopes: List[str]):
    if platform == Platform.MICROSOFT.value:
        url = (InitialMicrosoftGraphURLs.BASE_URL.value + InitialMicrosoftGraphURLs.AUTHORIZE.value).format(
            tenant=os.environ.get('MICROSOFT_TENANT_ID')
        )
    elif platform == Platform.GOOGLE.value:
        url = ''  # todo need to change
    elif platform == Platform.JIRA.value:
        url = ''  # todo need to change
    else:
        return
    req = PreparedRequest()
    req.prepare_url(url, params=generate_json_for_microsoft_code(platform, scopes))
    return dict(url=req.url)


def create_dict(dict_string: str):
    scopes_dict = {}
    for scope in dict_string.split():
        if scope == 'offline_scope':
            pass
        scopes_dict[scope] = True
    print(scopes_dict)
    return scopes_dict


def recreate_expires_at(seconds: int):
    current_time_stamp = datetime.utcnow().timestamp().__int__()
    return current_time_stamp + seconds


def update_data(data, service: ListCreateUpdateRetriveDeleteService, user_service: UserService, user: dict):
    user_from_db = user_service.get_by_email(user['email'])
    if not user_from_db:
        user_from_db = user_service.create({
            'email': user['email'],
            'access_token': user['access_token'],
            'expires_at': user['expires_at'],
        })
    microsoft_token = UserAPI(data['access_token'])
    ms_user = microsoft_token.get_user()

    service.create({
        'user_id': user_from_db.id,
        'email': ms_user['mail'],
        'account_id': ms_user['id'],
        'display_name': ms_user['displayName'],
        'access_token': ms_user['access_token'],
        'refresh_token': ms_user['refresh_token'],
        'scopes': create_dict(ms_user['scopes']),
        'expires_at': ms_user['expires_in']
    })


def authorize_user(code, service: ListCreateUpdateRetriveDeleteService, user_service: UserService, user: dict):
    base_url = InitialMicrosoftGraphURLs.BASE_URL.value.format(tenant=os.environ.get('MICROSOFT_TENANT_ID'))
    url = base_url + InitialMicrosoftGraphURLs.TOKEN_URL.value
    data = generate_json_for_token(Platform.MICROSOFT.value, code)

    response = requests.post(url=url, data=data)
    response_data = response.json()
    print(response_data)
    print(user, user['email'])
    if 'error' not in response_data.keys():
        response_data['expires_in'] = recreate_expires_at(response_data['expires_in'])
        update_data(response_data, service, user_service, user)
    return response_data
