import logging
import uuid
from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import session

from src.base.services import ListCreateUpdateRetriveDeleteService

from .models import JiraUser, JiraResouces

logger = logging.getLogger(__name__)

class JiraUserService(ListCreateUpdateRetriveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, JiraUser, 'id')
        
    def get_by_userId(self, userId: uuid.UUID) -> Query:
        return self.get(user_id=userId)
    
class JiraResouceService(ListCreateUpdateRetriveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, JiraResouces, 'id')
    
    def get_by_userId(self, userId: uuid.UUID) -> Query:
        return self.get(user_id=userId)
    # def check_resource_existence(self, obj: [dict]) -> bool:
    #     ids = [item['id'] for item in obj]
    #     existing_ids = self.db.query(JiraResouces.account_id).filter(JiraResouces.account_id.in_(ids)).all()
    #     existing_ids = [item[0] for item in existing_ids]
    #     new_ids = set(ids) - set(existing_ids)
        
    #     return False
