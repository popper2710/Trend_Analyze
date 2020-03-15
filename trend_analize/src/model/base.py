import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from ..db import Base, ENGINE


class ModelBase:
    __tablename__ = ""
    id = Column("id", Integer, primary_key=True)
    Int = Integer
    Col =
    Float =
