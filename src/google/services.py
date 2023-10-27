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

    def get_unset_deafult_stmt(self, user_id: uuid.UUID):
        return (
            update(self.model_class)
            .where(
                and_(
                    getattr(self.model_class, "user_id") == user_id,
                    getattr(self.model_class, "default") == True,
                )
            )
            .values(default=False)
        )

    def unset_and_set_default(self, user_id: uuid.UUID, email: str):
        unset_stmt = self.get_unset_deafult_stmt(user_id)
        set_stmt = (
            update(self.model_class)
            .where(
                and_(
                    self.model_class.user_id == user_id,
                    self.model_class.email == email,
                )
            )
            .values(default=True)
        )

        with self.db.begin():
            self.db.execute(unset_stmt)
            self.db.execute(set_stmt)

    def unset_default_and_create_or_update(self, obj) -> Query:
        unset_stmt = self.get_unset_deafult_stmt(obj["user_id"])
        try:
            existing_record = self.get(user_id=obj["user_id"], email=obj["email"])
            if existing_record:
                for key, value in obj.items():
                    setattr(existing_record, key, value)
            with self.db.begin():
                self.db.execute(unset_stmt)
                merged = self.db.merge(existing_record or self.model_class(**obj))
                self.db.flush()
                self.db.refresh(merged)
            self.logger.info(
                f"Created or updated {self.model_class} with parameters {obj}"
            )
            return merged
        except (IntegrityError, SQLAlchemyError) as e:
            self.handle_sqlalchemy_error(e, self.model_class)
