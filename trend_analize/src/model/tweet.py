import sys
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sadm
from ..db import Base, ENGINE


class Tweet:
    __tablename__ = "tweet"
    id = sa.Column('id', sa.Integer, primary_key=True)
    user_id = sa.Column('user_id', sa.Integer(20))
    created_at = sa.Column('created_at', sa.DateTime)
    text = sa.Column('created_at', sa.String(300))
    truncate = sa.Column('truncate', sadm.BIT(1))
    hashtags = sa.Column('hashtags', sa.String(200))
    
