import sys
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sadm
from db import Base, ENGINE


class Tweet(Base):
    """
    Tweet Model
    """
    __tablename__ = "tweet"

    id                    = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id              = sa.Column('tweet_id', sa.Integer)
    user_id               = sa.Column('user_id', sa.Integer)
    entities_id           = sa.Column('entities_id', sa.Integer)
    name                  = sa.Column('name', sa.String(100))
    created_at            = sa.Column('created_at', sa.DateTime)
    text                  = sa.Column('created_at', sa.String(300))
    lang                  = sa.Column('lang', sa.String(10))
    retweet_count         = sa.Column('retweet_count', sa.Integer)
    favorite_count        = sa.Column('favorite_count', sa.Integer)
    source                = sa.Column('source', sa.String(50))
    in_reply_to_status_id = sa.Column('in_reply_to_status_id', sa.Integer)
    coordinates           = sa.Column('coordinates', sadm.JSON())
    place                 = sa.Column('place', sadm.JSON())


class Entity(Base):
    """
    Entity Model
    """
    id                    = sa.Column('id', sa.Integer, primary_key=True)
    urls                  = sa.Column('urls', sadm.JSON())
    hashtags              = sa.Column('hashtags', sadm.JSON())
    user_mentions         = sa.Column('user_mentions', sadm.JSON())
    urls                  = sa.Column('urls', sadm.JSON())
    symbols               = sa.Column('symbols', )

def main():
    Base.metadata.create_all(bind=ENGINE)


if __name__ == '__main__':
    main()
