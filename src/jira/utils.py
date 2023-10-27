from fastapi import Depends
from datetime import datetime, timedelta

from src.base.services import UserService
from src.jira.dependencies import get_jira_user_service, get_resource_service, get_user_service
from src.jira.services import JiraResouceService, JiraUserService


def str2dict(scopes: str) -> dict:
    return {s: True for s in scopes.split()}

def dict2str(scopes: dict) -> str:
    return ' '.join(k for k in scopes.keys())

def seconds2currentTime(expires_in_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=expires_in_seconds) - timedelta(minutes=1)

def get_new_resource_from(old_res, new_res):
    if old_res:
        set1 = set(old_res)
        set2 = set(new_res)
        return set1.difference(set2)
    return new_res[0]

async def validate_scope_for_email(
    scopes: str,
    email: str,
    user_service: UserService,
    jira_user_service: JiraUserService,
    resource_service: JiraResouceService,
    client
):
    
    scopes = str2dict(scopes)
    
    user = user_service.get_by_email(email)
    if user is None:
        return False, False, False
    
    jira_user = jira_user_service.get_by_userId(user.id)
    if jira_user is None:
        return False, False, False

    # todo
    # have to update for multiple resource here
    resource = resource_service.get_by_userId(user.id)
    
    for scope, _ in scopes.items():
        if scope not in resource.scopes or resource.scopes[scope] is False:
            return resource, _, False
    
    # todo
    # have to handle when refresh token is invalid
    if resource.expires_at < datetime.now():
        token_data = await client.get_jira_rotational_token(resource.refresh_token, resource.scopes)
        resource.access_token = token_data['access_token']
        resource.refresh_token = token_data['refresh_token']
        resource.expires_at = seconds2currentTime(token_data['expires_in'])
        resource.scopes = str2dict(token_data['scope'])
        resource_service.update(resource)
    return resource, jira_user, True