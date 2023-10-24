from .models import GoogleToken
from src.base.services import ListCreateUpdateRetriveDeleteService
from sqlalchemy.orm import session


class GoogleTokenService(ListCreateUpdateRetriveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, GoogleToken, 'id')

    def get_access_token(self, user_id: int, scope: str, email: str) -> bool:
        # get token or refresh token or none if not found with scope
        self.get(user_id=user_id)
        return True