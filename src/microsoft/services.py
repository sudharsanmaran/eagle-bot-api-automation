import logging

from sqlalchemy.orm import session

from src.base.services import ListCreateUpdateRetrieveDeleteService
from src.microsoft.models import MicrosoftToken

logger = logging.getLogger(__name__)


class MicrosoftTokenService(ListCreateUpdateRetrieveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, MicrosoftToken, 'id')

