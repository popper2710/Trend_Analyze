from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from ..config import secret


DATABASE = "mysql://{host}:{port}@{user}/{database}?charset=utf8".format(
    host=secret.DB_HOST,
    port=secret.DB_PORT,
    user=secret.DB_PASSWORD,
    database=secret.DATABASE,
)

ENGINE = create_engine(
    DATABASE,
    encoding="utf-8",
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

