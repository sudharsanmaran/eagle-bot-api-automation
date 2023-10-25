from fastapi import Depends
from datetime import datetime, timedelta

from src.base.services import UserService
from src.jira.dependencies import get_jira_user_service, get_resource_service, get_user_service
from src.jira.services import JiraResouceService, JiraUserService


def str2dict(scopes: str) -> dict:
    scope = scopes.split()
    return {s: True for s in scope}

def seconds2currentTime(expires_in_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=expires_in_seconds) - timedelta(minutes=1)

def validate_scope_for_email(
    scopes: str,
    email: str,
    user_service: UserService,
    jira_user_service: JiraUserService,
    resource_service: JiraResouceService
) -> bool:
    
    scopes = str2dict(scopes)
    
    user = user_service.get_by_email(email)
    if user is None:
        return False
    
    jira_user = jira_user_service.get_by_userId(user.id)
    if jira_user is None:
        return False

    # todo
    # have to update for multiple resource here
    resource = resource_service.get_by_userId(jira_user.id)
    if resource is None:
        return False
    # check token expiry
    resource.access_token
    
    for scope, _ in scopes.items():
        if scope not in resource.scopes or resource.scopes[scope] is False:
            return False

    return True