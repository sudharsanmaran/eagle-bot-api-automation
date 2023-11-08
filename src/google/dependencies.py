from fastapi import Depends
from sqlalchemy.orm import Session

from src.base.services import UserService
from src.database import get_db
from .services import GoogleTokenService


def token_service(db: Session = Depends(get_db)):
    return GoogleTokenService(db)


def user_service(db: Session = Depends(get_db)):
    return UserService(db)
