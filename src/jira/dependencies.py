from fastapi import Depends
from sqlalchemy.orm import Session

from src.base.services import UserService

from ..database import get_db
from .services import JiraUserService, JiraResouceService

def get_jira_user_service(db: Session = Depends(get_db)):
    return JiraUserService(db)

def get_resource_service(db: Session = Depends(get_db)):
    return JiraResouceService(db)

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)