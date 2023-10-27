from datetime import datetime
import uuid
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CreateProjectRequest(BaseModel):
    description: str = Field("", description="A brief description of the project.")
    key: str = Field(
        ...,
        max_length=10,
        description="Project keys must be unique and start with an uppercase letter followed by one or more uppercase alphanumeric characters. The maximum length is 10 characters.",
    )
    name: str = Field(..., description="The name of the project")


class CreateIssueRequest(BaseModel):
    summary: str = Field(..., description="The summary of the issue.")
    project: int = Field(
        None,
        description="The project of the issue",
    )
    issuetype: int = Field(None, description="The issue type of the issue")


class JiraUserSchemas(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    account_id: str
    display_name: str
    access_token: str
    refresh_token: str
    scopes: dict
    default: bool
    expires_at: datetime
    model_config = ConfigDict(from_attributes=True)


class JiraResoucesSchemas(BaseModel):
    user_id: uuid.UUID
    resource_id: str
    resource_name: str
    avatar_url: str
    default: bool
    model_config = ConfigDict(from_attributes=True)
