import os
from datetime import datetime
from typing import List

import requests
from requests import PreparedRequest

from src.microsoft.decorators import Authorization
from src.base.services import ListCreateUpdateRetrieveDeleteService, UserService
from src.microsoft import InitialMicrosoftGraphURLs
from src.microsoft.client import UserAPI
from src.microsoft.methods import generate_json_for_microsoft_code, generate_json_for_token
from ..base.schemas import Response, Detail


@Authorization
def get_access_token_or_url(scopes: List[str]):
    url = (InitialMicrosoftGraphURLs.BASE_URL.value + InitialMicrosoftGraphURLs.AUTHORIZE.value).format(
        tenant=os.environ.get('MICROSOFT_TENANT_ID')
    )
    req = PreparedRequest()
    req.prepare_url(url, params=generate_json_for_microsoft_code(scopes))
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


def update_data(data, service: ListCreateUpdateRetrieveDeleteService, user_service: UserService, user: dict):
    user_from_db = user_service.get_by_email(user[0]['email'])
    if not user_from_db:
        user_from_db = user_service.create({
            'email': user[0]['email'],
            'access_token': user[1],
            'expires_at': user[0]['exp'],
        })
    microsoft_token = UserAPI(data['access_token'])
    ms_user = microsoft_token.get_user()

    print(ms_user)

    service.create({
        'user_id': user_from_db.id,
        'email': ms_user['mail'],
        'account_id': ms_user['id'],
        'display_name': ms_user['displayName'],
        'access_token': data['access_token'],
        'refresh_token': data['refresh_token'],
        'scopes': create_dict(data['scope']),
        'expires_at': data['expires_in']
    })


def authorize_user(code, service: ListCreateUpdateRetrieveDeleteService, user_service: UserService, user: dict):
    base_url = InitialMicrosoftGraphURLs.BASE_URL.value.format(tenant=os.environ.get('MICROSOFT_TENANT_ID'))
    url = base_url + InitialMicrosoftGraphURLs.TOKEN_URL.value
    data = generate_json_for_token(code)

    response = requests.post(url=url, data=data)
    response_data = response.json()
    print(response_data)
    # print(user, user[0]['email'])
    if 'error' not in response_data.keys():
        response_data['expires_in'] = recreate_expires_at(response_data['expires_in'])
        update_data(response_data, service, user_service, user)
    return response_data


def prepare_response(data: dict, status_code, message='', ):
    detail = Detail(message=message, data=data)
    response = Response(status_code=status_code, detail=detail)
    return response
