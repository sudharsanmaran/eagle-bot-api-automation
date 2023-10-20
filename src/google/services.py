from .models import GoogleToken
from src.base.services import ListCreateUpdateRetriveDeleteService
from sqlalchemy.orm import session


class GoogleTokenService(ListCreateUpdateRetriveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, GoogleToken, 'id')

    def get_access_token(scope: str):
        pass