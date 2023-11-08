from .models import GoogleToken
from src.base.services import ListCreateUpdateRetrieveDeleteService
from sqlalchemy.orm import session


class GoogleTokenService(ListCreateUpdateRetrieveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, GoogleToken, "id")

    def get_access_token(self, **filters):
        return self.get(**filters)
