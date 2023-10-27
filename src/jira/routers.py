from datetime import datetime
import os
from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from src.auth import JWTBearer
from .client import JiraClient

from src.base.schemas import User
from src.jira.schemas import (
    CreateIssueRequest,
    JiraResoucesSchemas,
    JiraUserSchemas,
    CreateProjectRequest,
)

from src.base.services import UserService
from src.jira.services import JiraResouceService, JiraUserService

from src.jira.dependencies import (
    get_resource_service,
    get_jira_user_service,
    get_user_service,
)

from src.jira.utils import (
    dict2str,
    get_new_resource_from,
    validate_scope_for_email,
    str2dict,
    seconds2currentTime,
)
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
    # jira_token_res = await client.exchange_code_for_tokens(code)
    jira_token_res = {
        "access_token": "eyJraWQiOiJmZTM2ZThkMzZjMTA2N2RjYTgyNTg5MmEiLCJhbGciOiJSUzI1NiJ9.eyJqdGkiOiJmNjkxNDU3MS04ZmUyLTRmNGEtOGMyNy0xOGQ3ZTJkZDhiODkiLCJzdWIiOiI3MTIwMjA6YWFhNDhiZjItODNmZi00ZTQ0LTgzNWUtNzBmOGFiZTAwNDdhIiwibmJmIjoxNjk4Mzg4NDQxLCJpc3MiOiJodHRwczovL2F1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTY5ODM4ODQ0MSwiZXhwIjoxNjk4MzkyMDQxLCJhdWQiOiJxRmV0eGZIQ21INnlmOHBiZlN5ZzNFMzZkYmV4eXRDTyIsInNjb3BlIjoibWFuYWdlOmppcmEtY29uZmlndXJhdGlvbiBvZmZsaW5lX2FjY2VzcyByZWFkOm1lIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL3N5c3RlbUFjY291bnRFbWFpbCI6ImRlZGJjOGQzLTA3ZjEtNGUxMS05NDZkLTJjM2JhYTM4MDFjMEBjb25uZWN0LmF0bGFzc2lhbi5jb20iLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vYXRsX3Rva2VuX3R5cGUiOiJBQ0NFU1MiLCJodHRwczovL2F0bGFzc2lhbi5jb20vZmlyc3RQYXJ0eSI6ZmFsc2UsImh0dHBzOi8vYXRsYXNzaWFuLmNvbS92ZXJpZmllZCI6dHJ1ZSwiY2xpZW50X2lkIjoicUZldHhmSENtSDZ5ZjhwYmZTeWczRTM2ZGJleHl0Q08iLCJodHRwczovL2F0bGFzc2lhbi5jb20vc3lzdGVtQWNjb3VudElkIjoiNzEyMDIwOmRhNzY5M2I2LTQyNTctNDk3ZS1iNjI0LThlNjQxY2YxMTNlYiIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL2VtYWlsRG9tYWluIjoiZ21haWwuY29tIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tLzNsbyI6dHJ1ZSwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL29hdXRoQ2xpZW50SWQiOiJxRmV0eGZIQ21INnlmOHBiZlN5ZzNFMzZkYmV4eXRDTyIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS92ZXJpZmllZCI6dHJ1ZSwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3VqdCI6IjNkOGY3Mjg3LTI0M2EtNDBjNC04ZGM2LTg5MGE1NmQ1M2FiYiIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9zZXNzaW9uX2lkIjoiNjdlZTkzZTktYzM5OS00YmRhLTllYzQtOTBkZWVlOTFjYzUzIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL3N5c3RlbUFjY291bnRFbWFpbERvbWFpbiI6ImNvbm5lY3QuYXRsYXNzaWFuLmNvbSJ9.kSxBcNvFstb_mLxNGc2NyTpp4E538t1nKWCmBg16z3JzwuiodhozRlA5DIu8zS8VEnsm3OA0O_6wLswTUIU5RpVWlev0EKhwp9Yepyjv0vW96ViPybCu-S3_MnekBRhKaEfFKb31LReuKqr2ElLiaWi9tAmqIh2SXp7viU8RN1VgtJqJDN8L_WuMPRqCQk0ep6dasXcQOvlFWZz-jGQNJRgylQbGy1zQ3Xdan_41O2JAyQsgAOJPhivOYLRe9GR7aYUapi1AuzzWjKr6VaDslAFIqQ8FWHNXdqTJ2cMdobQyRDm4WyJmxD7pXUOAuRw3dy9GeDNZVM6GeX5NjQ1KiA",
        "scope": "manage:jira-configuration offline_access read:me",
        "refresh_token": "eyJraWQiOiI1MWE2YjE2MjRlMTQ5ZDFiYTdhM2VmZjciLCJhbGciOiJSUzI1NiJ9.eyJqdGkiOiI3MDExNmZlMC1iMWUwLTQyOTItOGRhZS0yZjZmYjc1NTk2YzQiLCJzdWIiOiI3MTIwMjA6YWFhNDhiZjItODNmZi00ZTQ0LTgzNWUtNzBmOGFiZTAwNDdhIiwibmJmIjoxNjk4Mzg4NDQxLCJpc3MiOiJodHRwczovL2F1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTY5ODM4ODQ0MSwiZXhwIjoxNzA2MTY0NDQxLCJhdWQiOiJxRmV0eGZIQ21INnlmOHBiZlN5ZzNFMzZkYmV4eXRDTyIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9hdGxfdG9rZW5fdHlwZSI6IlJPVEFUSU5HX1JFRlJFU0giLCJ2ZXJpZmllZCI6InRydWUiLCJzY29wZSI6Im1hbmFnZTpqaXJhLWNvbmZpZ3VyYXRpb24gb2ZmbGluZV9hY2Nlc3MgcmVhZDptZSIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3BhcmVudF9hY2Nlc3NfdG9rZW5faWQiOiJmNjkxNDU3MS04ZmUyLTRmNGEtOGMyNy0xOGQ3ZTJkZDhiODkiLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vdmVyaWZpZWQiOnRydWUsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS91anQiOiIzZDhmNzI4Ny0yNDNhLTQwYzQtOGRjNi04OTBhNTZkNTNhYmIiLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vcmVmcmVzaF9jaGFpbl9pZCI6InFGZXR4ZkhDbUg2eWY4cGJmU3lnM0UzNmRiZXh5dENPLTcxMjAyMDphYWE0OGJmMi04M2ZmLTRlNDQtODM1ZS03MGY4YWJlMDA0N2EtNzQwZDBmNWQtOGVjMC00MzA5LWFjZWItMjY2NDQxNTg1YzdiIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3Nlc3Npb25faWQiOiI2N2VlOTNlOS1jMzk5LTRiZGEtOWVjNC05MGRlZWU5MWNjNTMifQ.LgrZvKYb-GCmTjyqhy9KgDelXzAGAYhum96X2JeB4F1xueCTfw6R4LP7XWXOTUTZEAfrZnGCwyFXfcCq39Gt1gZp9uhUt7YwvX5oGsrB5nNC9Rn3OWRRrd9GzG-DE0A4kpblNASRlbWTv-Oo_dkCi4l1sq-G720jMLTtaNFCpiR8fm6cz4ph0Y5YKkpaWfvyKYKvr88LTAy94EGmL1XDMhr8-jPm65tRc0kNnsfsFtbkPEfDxjMLJOL2TAP-8g2VmCuMRmJmfsbQZ1J1JnvN2WdP-8XeDHesnHB4WEJ2HS1dAzNp630LtQTxwO2RDyhYbDaABXoGAf7f1gQybiqwig",
        "expires_in": 1600,
    }

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
        access_token=jira_token_res["access_token"],
        refresh_token=jira_token_res["refresh_token"],
        default=True,
        scopes=str2dict(jira_token_res["scope"]),
        expires_at=seconds2currentTime(jira_token_res["expires_in"]),
    )
    jira_user = jira_user_service.unset_default_and_create_or_update(
        jira_user_data.model_dump()
    )

    existed_user_resouces = jira_resouce_service.get_by_userId(jira_user.id)
    new_resource = get_new_resource_from(existed_user_resouces, user_resouces_res)
    jira_resouce_data = JiraResoucesSchemas(
        user_id=jira_user.id,
        resource_id=new_resource["id"],
        resource_name=new_resource["name"],
        default=True,
        avatar_url=new_resource["avatarUrl"],
    )
    jira_resouce_service.unset_default_create(jira_resouce_data.model_dump())

    return {"status": "ok"}


@jira_router.post("/create-project")
async def create_project(
    data: CreateProjectRequest,
    token_data=Depends(JWTBearer()),
    user_service: UserService = Depends(get_user_service),
    jira_user_service: JiraUserService = Depends(get_jira_user_service),
    resource_service: JiraResouceService = Depends(get_resource_service),
) -> Any:
    scope = f"{JiarScope.BASIC} {JiarScope.MANAGE_JIRA_CONF}"

    resource, jira_user, verify = await validate_scope_for_email(
        scope,
        token_data[0]["email"],
        user_service,
        jira_user_service,
        resource_service,
        client,
    )
    if not verify:
        if resource:
            scope = f"{dict2str(resource.scopes)} {scope}"
        return await client.get_consent_url(scope, "Access_denied")

    project = await client.create_project(resource, jira_user, data.model_dump())
    return {"status": "ok", "details": project}


@jira_router.post("/create-issue")
async def create_issue(
    data: CreateIssueRequest,
    token_data=Depends(JWTBearer()),
    user_service: UserService = Depends(get_user_service),
    jira_user_service: JiraUserService = Depends(get_jira_user_service),
    resource_service: JiraResouceService = Depends(get_resource_service),
) -> Any:
    scope = f"{JiarScope.BASIC} {JiarScope.WRITE_JIRA_WORK}"

    resource, jira_user, verify = await validate_scope_for_email(
        scope,
        token_data[0]["email"],
        user_service,
        jira_user_service,
        resource_service,
        client,
    )
    if not verify:
        if resource:
            scope = f"{dict2str(resource.scopes)} {scope}"
        return await client.get_consent_url(scope, "Access_denied")

    issue = await client.create_issue(resource, jira_user, data.model_dump())
    return {"status": "ok", "details": issue}
