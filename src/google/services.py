import uuid

from fastapi import Query
from .models import GoogleToken
from src.base.services import ListCreateUpdateRetriveDeleteService
from sqlalchemy.orm import session


class GoogleTokenService(ListCreateUpdateRetriveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, GoogleToken, 'id')

    def get_access_token(self, user_id: uuid.UUID, email: str = None):
        return self.get(user_id=user_id)