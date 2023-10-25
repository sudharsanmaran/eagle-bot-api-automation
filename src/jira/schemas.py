from datetime import datetime
import uuid
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.jira.constants import AssTypeEnum, ProjTempKeyEnum, ProjTypeKeyEnum


class CreateProjectRequest(BaseModel):
    assigneeType: AssTypeEnum = Field(
        "UNASSIGNED",
        description="The default assignee when creating issues for this project.",
    )
    avatarId: int = Field(
        None, description="An integer value for the project's avatar."
    )
    categoryId: int = Field(
        None,
        description="The ID of the project's category. A complete list of category IDs is found using the Get all project categories operation.",
    )
    description: str = Field("", description="A brief description of the project.")
    issueSecurityScheme: int = Field(
        None,
        description="The ID of the issue security scheme for the project, which enables you to control who can and cannot view issues. Use the Get issue security schemes resource to get all issue security scheme IDs.",
    )
    key: str = Field(
        ...,
        max_length=10,
        description="Project keys must be unique and start with an uppercase letter followed by one or more uppercase alphanumeric characters. The maximum length is 10 characters.",
    )
    leadAccountId: str = Field(
        None,
        max_length=128,
        description="The account ID of the project lead. Max length 128",
    )
    name: str = Field(..., description="The name of the project")
    notificationScheme: int = Field(
        None,
        description="The ID of the notification scheme for the project. Use the Get notification schemes resource to get a list of notification scheme IDs.",
    )
    permissionScheme: int = Field(
        None,
        description="The ID of the permission scheme for the project. Use the Get all permission schemes resource to see a list of all permission scheme IDs.",
    )
    projectTemplateKey: ProjTempKeyEnum = Field(
        ProjTempKeyEnum.GREENHOPPER_BASIC,
        description="A predefined configuration for a project. The type of the projectTemplateKey must match with the type of the projectTypeKey.",
    )
    projectTypeKey: ProjTypeKeyEnum = Field(
        ProjTypeKeyEnum.SOFTWARE, description="The key of the project type"
    )
    url: str = Field(
        None,
        description="A link to information about this project, such as project documentation",
    )

class JiraUserSchemas(BaseModel):
    user_id: uuid.UUID 
    email: EmailStr
    account_id: str
    display_name: str
    model_config = ConfigDict(from_attributes=True)
    
class JiraResoucesSchemas(BaseModel):
    user_id: uuid.UUID
    resource_id: str
    resource_name: str
    access_token: str
    refresh_token: str
    scopes: dict
    expires_at: datetime
    model_config = ConfigDict(from_attributes=True)