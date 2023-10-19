import logging
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.query import Query
from typing import List, Type
from cachetools import cached, TTLCache

logger = logging.getLogger(__name__)

cache = TTLCache(maxsize=100, ttl=300) 


def handle_sqlalchemy_error(error: SQLAlchemyError, model_name: str):
    error_message = "An error occurred while logging this request to database."
    logger.error(f"Error with model {model_name}: {error}")
    raise HTTPException(status_code=400, detail=error_message)


class ListCreateUpdateRetriveDeleteService:
    def __init__(self, db: Session, model_class: Type, primary_key_name: str):
        self.db = db
        self.model_class = model_class
        self.primary_key_name = primary_key_name
    
    @cached(cache)
    def get(self, **kwargs) -> Query:
        try:
            stmt = select(self.model_class).where(
                and_(*(getattr(self.model_class, key) ==
                     value for key, value in kwargs.items()))
            )

            with self.db:
                results = self.db.bulk_query(stmt).all()
            return results
        except NoResultFound:
            logger.info(
                f"No result found for model {self.model_class} with parameters {kwargs}")
            return None

    def get_by_primary_key(self, primary_key_value) -> Query:
        try:
            stmt = select(self.model_class).where(
                getattr(self.model_class, self.primary_key_name) == primary_key_value)

            with self.db:
                result = self.db.execute(stmt).scalar_one()
            return result
        except NoResultFound:
            logger.info(
                f"No result found for model {self.model_class} with primary key {primary_key_value}")
            return None

    def list(self, limit: int = 10, offset: int = 0) -> List[Query]:
        try:
            stmt = select(self.model_class).offset(offset).limit(limit)

            with self.db:
                results = self.db.bulk_query(stmt).all()
            return results
        except SQLAlchemyError as e:
            handle_sqlalchemy_error(e, self.model_class)

    def create(self, obj) -> Query:
        try:
            obj = self.model_class(**obj)
            with self.db.begin():
                self.db.merge(obj)
            logger.info(
                f"Created new {self.model_class} with parameters {obj}")
            return obj
        except (IntegrityError, SQLAlchemyError) as e:
            handle_sqlalchemy_error(e, self.model_class)

    def update(self, existing_record, obj) -> Query:
        try:
            if existing_record:
                for key, value in obj.items():
                    setattr(existing_record, key, value)
            with self.db.begin():
                self.db.merge(existing_record)
            logger.info(f"Updated {self.model_class} with parameters {obj}")
            return existing_record
        except (IntegrityError, SQLAlchemyError) as e:
            handle_sqlalchemy_error(e, self.model_class)

    def create_or_update(self, obj, lookup_field=None) -> Query:
        try:
            if lookup_field:
                existing_record = self.get(**{lookup_field: obj[lookup_field]})
            else:
                existing_record = self.get_by_primary_key(
                    obj[self.primary_key_name])
            if existing_record:
                for key, value in obj.items():
                    setattr(existing_record, key, value)
            with self.db.begin():
                self.db.merge(existing_record or self.model_class(**obj))
            self.db.flush()
            logger.info(
                f"Created or updated {self.model_class} with parameters {obj}")
            return existing_record or self.model_class(**obj)
        except (IntegrityError, SQLAlchemyError) as e:
            handle_sqlalchemy_error(e, self.model_class)
            
    def delete(self, objs: List) -> None:
        try:
            with self.db.begin():
                self.db.bulk_delete(objs)
            logger.info(f"Deleted {len(objs)} {self.model_class} records")
        except (IntegrityError, SQLAlchemyError) as e:
            handle_sqlalchemy_error(e, self.model_class)
