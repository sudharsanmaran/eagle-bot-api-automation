from datetime import datetime, timedelta

from src.base.services import UserService
from src.jira.services import JiraResouceService, JiraUserService


def str2dict(scopes: str) -> dict:
    return {s: True for s in scopes.split()}


def dict2str(scopes: dict) -> str:
    return ' '.join(k for k in scopes.keys())


def seconds2currentTime(expires_in_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=expires_in_seconds) - timedelta(minutes=1)


def get_new_resource_from(old_res, new_res):
    if old_res:
        ids = [str(obj.resource_id) for obj in old_res]
        return [d['id'] for d in new_res if d['id'] not in ids]
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
        return {'verify': False}
    jira_user = jira_user_service.get_default_user(user.id)
    if jira_user is None:
        return {'verify': False}

    resource = resource_service.get_default_user(jira_user.id)

    for scope, _ in scopes.items():
        if scope not in jira_user.scopes or jira_user.scopes[scope] is False:
            return {'scopes': jira_user.scopes, 'verify': False}
    # todo
    # have to handle when refresh token is invalid
    if jira_user.expires_at < datetime.now():
        token_data = await client.get_jira_rotational_token(jira_user.refresh_token, jira_user.scopes)
        jira_user.access_token = token_data['access_token']
        jira_user.refresh_token = token_data['refresh_token']
        jira_user.expires_at = seconds2currentTime(token_data['expires_in'])
        jira_user.scopes = str2dict(token_data['scope'])
        jira_user_service.update(jira_user)
    return {'resource': resource, 'jira_user': jira_user, 'verify': True}
