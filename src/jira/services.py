import uuid
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import session

from src.base.services import ListCreateUpdateRetrieveDeleteService

from .models import JiraUser, JiraResouces


class JiraUserService(ListCreateUpdateRetrieveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, JiraUser, "id")

    def get_default_user(self, userId: uuid.UUID) -> Query:
        return self.get(user_id=userId, default=True)


class JiraResouceService(ListCreateUpdateRetrieveDeleteService):
    def __init__(self, db: session):
        super().__init__(db, JiraResouces, "id")

    def get_default_user(self, userId: uuid.UUID) -> Query:
        return self.get(user_id=userId, default=True)

    def unset_default_create(self, obj) -> Query:
        unset_stmt = self.get_unset_deafult_stmt(obj["user_id"])
        try:
            with self.db.begin():
                self.db.execute(unset_stmt)
                merged = self.db.merge(self.model_class(**obj))
                self.db.flush()
                self.db.refresh(merged)
            self.logger.info(
                f"Created or updated {self.model_class} with parameters {obj}"
            )
            return merged
        except (IntegrityError, SQLAlchemyError) as e:
            self.handle_sqlalchemy_error(e, self.model_class)
