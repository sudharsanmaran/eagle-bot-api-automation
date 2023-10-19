from sqlalchemy.orm import sessionmaker, session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import os

Base = declarative_base()

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
sslmode = "require"
port = os.getenv('DB_PORT')


# database_url = f'postgresql+psycopg://{username}:{password}@{host}:{port}/{database}?sslmode={sslmode}'
database_url = f'postgresql+psycopg://{username}:{password}@{host}:{port}/{database}'

# database_url = 'sqlite:///./test.db'


def get_db() -> session:
    global database_url

    local_session = sessionmaker(bind=create_engine(database_url, pool_size=5, max_overflow=0))
    db = local_session()
    try:
        yield db
    finally:
        db.close()
