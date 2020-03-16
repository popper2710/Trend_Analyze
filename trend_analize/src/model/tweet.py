import sys
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sadm
from ..db import Base, ENGINE


class Tweet:
    __tablename__ = "tweet"

    id = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id = sa.Column('tweet_id', sa.Integer(30))
    user_id = sa.Column('user_id', sa.Integer(30))
    entities_id = sa.Column('entities_id', sa.Integer(20))
    name = sa.Column('name', sa.String(100))
    created_at = sa.Column('created_at', sa.DateTime)
    text = sa.Column('created_at', sa.String(300))
    lang = sa.Column('lang', sa.String(10))
    retweet_count = sa.Column('retweet_count', sa.Integer(20))
    favorite_count = sa.Column('favorite_count', sa.Integer(20))
    source = sa.Column('source', sa.String(50))
    in_reply_to_status_id = sa.Column('in_reply_to_status_id', sa.Integer(30))
    coordinates = sa.Column('coordinates', sadm.JSON())
    place = sa.Column('place', sadm.JSON())


def main(args):
    Base.metadata.create_all(bind=ENGINE)

if __name__ == '__main__':
    main(sys.argv)
