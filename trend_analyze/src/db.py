import os

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from trend_analyze.config import secret

ENV = os.environ["TREND_ANALYZE_ENV"]

db_prefix = ""
if ENV == "test":
    db_prefix = "test_"

DATABASE_NAME = db_prefix + secret.DATABASE

DATABASE = "mysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
    user=secret.DB_NAME,
    password=secret.DB_PASSWORD,
    host=secret.DB_HOST,
    port=secret.DB_PORT,
    database=DATABASE_NAME
)

ENGINE = create_engine(
    DATABASE,
    echo=True
)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()
