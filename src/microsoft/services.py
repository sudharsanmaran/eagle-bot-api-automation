from src.base.services import ListCreateUpdateRetriveDeleteService
from sqlalchemy.orm import session

from src.microsoft.models import MicrosoftToken


class MicrosoftTokenService(ListCreateUpdateRetriveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, MicrosoftToken, 'id')
