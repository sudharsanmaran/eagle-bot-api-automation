import uuid

from fastapi import Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, update
from .models import GoogleToken
from src.base.services import ListCreateUpdateRetrieveDeleteService
from sqlalchemy.orm import session


class GoogleTokenService(ListCreateUpdateRetrieveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, GoogleToken, "id")

    def get_access_token(self, user_id: uuid.UUID, email: str = None):
        return self.get(user_id=user_id)

