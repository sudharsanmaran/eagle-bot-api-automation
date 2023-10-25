import os
from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from src.auth import JWTBearer
from .client import JiraClient

from src.base.schemas import User
from src.jira.schemas import JiraResoucesSchemas, JiraUserSchemas, CreateProjectRequest

from src.base.services import UserService
from src.jira.services import JiraResouceService, JiraUserService

from src.jira.dependencies import (
    get_resource_service,
    get_jira_user_service,
    get_user_service,
)

from src.jira.utils import validate_scope_for_email, str2dict, seconds2currentTime
from src.jira.constants import JiarScope

jira_router = APIRouter(tags=["jira"], prefix="/jira")

client = JiraClient()


@jira_router.get("/callback")
async def Oauth2_callback(
    code: str,
    token_data=Depends(JWTBearer()),
    jira_user_service: JiraUserService = Depends(get_jira_user_service),
    user_service: UserService = Depends(get_user_service),
    jira_resouce_service: JiraResouceService = Depends(get_resource_service),
) -> Any:
    user_info, sso_token = token_data
    jira_token_res = await client.exchange_code_for_tokens(code)

    user_details_res = await client.get_Jira_user(jira_token_res["access_token"])
    user_resouces_res = await client.get_user_accessible_resources(
        jira_token_res["access_token"]
    )

    user_data = User(
        email=user_info["email"], access_token=sso_token, expires_at=user_info["exp"]
    )
    user = user_service.create_or_update(user_data.model_dump(), lookup_field="email")

    jira_user_data = JiraUserSchemas(
        user_id=user.id,
        email=user_details_res["email"],
        account_id=user_details_res["account_id"],
        display_name=user_details_res["name"],
    )
    jira_user = jira_user_service.create_or_update(
        jira_user_data.model_dump(), lookup_field="email"
    )
    # todo
    # later we have to update multiple resource for a user
    jira_resouce_data = JiraResoucesSchemas(
        user_id=jira_user.id,
        resource_id=user_resouces_res[0]["id"],
        resource_name=user_resouces_res[0]["name"],
        access_token=jira_token_res["access_token"],
        refresh_token=jira_token_res["refresh_token"],
        scopes=str2dict(jira_token_res["scope"]),
        expires_at=seconds2currentTime(jira_token_res["expires_in"]),
    )
    jira_resouce_service.create_or_update(
        jira_resouce_data.model_dump(), lookup_field="resource_id"
    )

    return {"status": "ok"}


@jira_router.post("/create-project")
async def create_project(
    data: CreateProjectRequest,
    token_data=Depends(JWTBearer()),
    user_service: UserService = Depends(get_user_service),
    jira_user_service: JiraUserService = Depends(get_jira_user_service),
    resource_service: JiraResouceService = Depends(get_resource_service),
) -> Any:
    scope = f"{JiarScope.BASIC} {JiarScope.CREATE_PROJECT}"

    verify = validate_scope_for_email(
        scope, token_data[0]["email"], user_service, jira_user_service, resource_service
    )

    if not verify:
        return await client.get_consent_url(scope)

    # project = await client.create_project(user_email, data.model_dump())
    return {"status": "ok"}
