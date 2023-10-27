import logging

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.base.services import ListCreateUpdateRetrieveDeleteService
from sqlalchemy.orm import session

from src.microsoft.models import MicrosoftToken

logger = logging.getLogger(__name__)


class MicrosoftTokenService(ListCreateUpdateRetrieveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, MicrosoftToken, 'id')

    def get_token_with_user_id(self, user_id):
        se = self.get(user_id=user_id)
        try:
            stmt = select(self.model_class).where(
                getattr(self.model_class, 'user_id') == user_id
            )

            with self.db:
                results = self.db.execute(stmt).scalar_one()
            return results
        except NoResultFound:
            logger.info(
                f"No result found for model {self.model_class} with parameters {user_id}")
            return None
