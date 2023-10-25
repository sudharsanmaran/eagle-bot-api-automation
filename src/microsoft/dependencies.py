from fastapi import Depends
from sqlalchemy.orm import Session

from src.database import get_db
from .services import MicrosoftTokenService
from ..base.services import UserService


def token_service(db: Session = Depends(get_db)):
    return MicrosoftTokenService(db)


def user_service(db: Session = Depends(get_db)):
    return UserService(db)
