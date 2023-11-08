from typing import Any
from fastapi import APIRouter, Depends
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
    jira_token_res = await client.exchange_code_for_tokens(code)
    # jira_token_res = {
    #     "access_token": "eyJraWQiOiJmZTM2ZThkMzZjMTA2N2RjYTgyNTg5MmEiLCJhbGciOiJSUzI1NiJ9.eyJqdGkiOiJmMTdlMzM3Mi02MDRiLTQ2MWQtYTZmMi1kYTIzZmQ3ZjEzMDIiLCJzdWIiOiI3MTIwMjA6YWFhNDhiZjItODNmZi00ZTQ0LTgzNWUtNzBmOGFiZTAwNDdhIiwibmJmIjoxNjk4NDAyNDU0LCJpc3MiOiJodHRwczovL2F1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTY5ODQwMjQ1NCwiZXhwIjoxNjk4NDA2MDU0LCJhdWQiOiJxRmV0eGZIQ21INnlmOHBiZlN5ZzNFMzZkYmV4eXRDTyIsInNjb3BlIjoibWFuYWdlOmppcmEtY29uZmlndXJhdGlvbiBvZmZsaW5lX2FjY2VzcyByZWFkOm1lIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL3N5c3RlbUFjY291bnRFbWFpbCI6ImRlZGJjOGQzLTA3ZjEtNGUxMS05NDZkLTJjM2JhYTM4MDFjMEBjb25uZWN0LmF0bGFzc2lhbi5jb20iLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vYXRsX3Rva2VuX3R5cGUiOiJBQ0NFU1MiLCJodHRwczovL2F0bGFzc2lhbi5jb20vZmlyc3RQYXJ0eSI6ZmFsc2UsImh0dHBzOi8vYXRsYXNzaWFuLmNvbS92ZXJpZmllZCI6dHJ1ZSwiY2xpZW50X2lkIjoicUZldHhmSENtSDZ5ZjhwYmZTeWczRTM2ZGJleHl0Q08iLCJodHRwczovL2F0bGFzc2lhbi5jb20vc3lzdGVtQWNjb3VudElkIjoiNzEyMDIwOmRhNzY5M2I2LTQyNTctNDk3ZS1iNjI0LThlNjQxY2YxMTNlYiIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS91anQiOiJkOWE4NjU0Yi05MjA1LTQzNDEtOWE0Zi1iMWVhOWZkYzMwOWMiLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vcHJvY2Vzc1JlZ2lvbiI6InVzLXdlc3QtMiIsImh0dHBzOi8vYXRsYXNzaWFuLmNvbS9lbWFpbERvbWFpbiI6ImdtYWlsLmNvbSIsImh0dHBzOi8vYXRsYXNzaWFuLmNvbS8zbG8iOnRydWUsImh0dHBzOi8vYXRsYXNzaWFuLmNvbS9vYXV0aENsaWVudElkIjoicUZldHhmSENtSDZ5ZjhwYmZTeWczRTM2ZGJleHl0Q08iLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vdmVyaWZpZWQiOnRydWUsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9zZXNzaW9uX2lkIjoiNjdlZTkzZTktYzM5OS00YmRhLTllYzQtOTBkZWVlOTFjYzUzIiwiaHR0cHM6Ly9hdGxhc3NpYW4uY29tL3N5c3RlbUFjY291bnRFbWFpbERvbWFpbiI6ImNvbm5lY3QuYXRsYXNzaWFuLmNvbSJ9.tcDvMjWTSPgqpnH-szo08ZicfrJbgHl3NipLxwU_K-fPe9oB2qMU2ldU85PvjOnXstAt_VcQDsRbn0VywPo_qjJ6xRvDtrNTcPV3ez7RwdV_msOhlKHkQ5pyp-cSEPi--WNrJPpCNlC0aWKXCd3Byviv8hdD07oJE-VNxmR8Dxtb86OIt-PmXbs8SUswFR0HHh7UNNQVSL20p9fFAirqrXMJmnFqjLUz07yHInyEQpnXPuEzTVLxGJr_EP6fC6vy-BWgSHrjYBk1pv_p9FV4-kFludJYSYCS1R5TjQp-6bsIhNAnpXcqQgLR7A-DyKQtRhZDGEoOcVR7vMXTcQFeig",
    #     "scope": "manage:jira-configuration offline_access read:me",
    #     "refresh_token": "eyJraWQiOiI1MWE2YjE2MjRlMTQ5ZDFiYTdhM2VmZjciLCJhbGciOiJSUzI1NiJ9.eyJqdGkiOiJhMjRlNDM1ZC04NTY2LTQ5MzUtYjZlMy1iNjlkMTUyMmU3NjgiLCJzdWIiOiI3MTIwMjA6YWFhNDhiZjItODNmZi00ZTQ0LTgzNWUtNzBmOGFiZTAwNDdhIiwibmJmIjoxNjk4Mzk2ODY0LCJpc3MiOiJodHRwczovL2F1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTY5ODM5Njg2NCwiZXhwIjoxNzA2MTcyODY0LCJhdWQiOiJxRmV0eGZIQ21INnlmOHBiZlN5ZzNFMzZkYmV4eXRDTyIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9hdGxfdG9rZW5fdHlwZSI6IlJPVEFUSU5HX1JFRlJFU0giLCJ2ZXJpZmllZCI6InRydWUiLCJzY29wZSI6Im1hbmFnZTpqaXJhLWNvbmZpZ3VyYXRpb24gb2ZmbGluZV9hY2Nlc3MgcmVhZDptZSIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3JlZnJlc2hfY2hhaW5faWQiOiJxRmV0eGZIQ21INnlmOHBiZlN5ZzNFMzZkYmV4eXRDTy03MTIwMjA6YWFhNDhiZjItODNmZi00ZTQ0LTgzNWUtNzBmOGFiZTAwNDdhLTk0ZGMzYWFmLTFlZDUtNDcwYi05MmI4LTIzMTc0MGVkOTZhNCIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS91anQiOiI2Y2I3ZTBkZS03OTA0LTQ0ZjktODBlNi00M2M2NGNjMzM5NDQiLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vcGFyZW50X2FjY2Vzc190b2tlbl9pZCI6IjQ0OGFiMmU1LTRjODctNDgxYy1hMGNjLWJjYTYwNjkxYTI5OCIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS92ZXJpZmllZCI6dHJ1ZSwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3Nlc3Npb25faWQiOiI2N2VlOTNlOS1jMzk5LTRiZGEtOWVjNC05MGRlZWU5MWNjNTMifQ.NxSVicUTXez-KDndL5u8Alj0iT1j3GNteTHn76DOv2a5rx0Cxaik1Znx7Zlzfgrbdq69_L8bTj7XBINFZjbHwhqMvjTj3E28NQuD8rd1TfV4kOiwo7fYhDfj_hbfZdcB1GH7mxp2AfQiS80ZRFH7bYZUExnRxjoWwnbMmYkD_-8-mZk38KNPZFj3xu_huV44HH4_9aMnIw-yMGrxFkZGtcwnRjUzbya4wP00AMyTvjw0CTYhF8a8vy25AS3rBPl4kISO75SI4JoORoBq274ZyUqKXOSTgN2x8xwgeD_7zMqCJNFppGwH1o2pGNJkJ7G_5pg2d4caiCFrJLjHrCV1YA",
    #     "expires_in": 1600,
    # }

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

    existed_user_resouces = jira_resouce_service.get_all(user_id=jira_user.id)
    new_resource = get_new_resource_from(existed_user_resouces, user_resouces_res)
    if new_resource:
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

    resource_and_jira_user_data = await validate_scope_for_email(
        scope,
        token_data[0]["email"],
        user_service,
        jira_user_service,
        resource_service,
        client,
    )
    if not resource_and_jira_user_data["verify"]:
        if resource_and_jira_user_data.get("resource"):
            scope = (
                f"{dict2str(resource_and_jira_user_data['resource'].scopes)} {scope}"
            )
        return await client.get_consent_url(scope, "Access_denied")

    project = await client.create_project(
        resource_and_jira_user_data["resource"].resource_id,
        resource_and_jira_user_data["jira_user"].account_id,
        resource_and_jira_user_data["jira_user"].access_token,
        data.model_dump(),
    )
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

    resource_and_jira_user_data = await validate_scope_for_email(
        scope,
        token_data[0]["email"],
        user_service,
        jira_user_service,
        resource_service,
        client,
    )
    if not resource_and_jira_user_data["verify"]:
        if resource_and_jira_user_data.get("resource"):
            scope = (
                f"{dict2str(resource_and_jira_user_data['resource'].scopes)} {scope}"
            )
        return await client.get_consent_url(scope, "Access_denied")

    issue = await client.create_issue(
        resource_and_jira_user_data["resource"],
        resource_and_jira_user_data["jira_user"],
        data.model_dump(),
    )
    return {"status": "ok", "details": issue}
