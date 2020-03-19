import sys
import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sadm
from sqlalchemy.orm import relationship
from db import Base, ENGINE


class Tweet(Base):
    """
    Tweet Model
    """
    __tablename__ = "tweet"

    id                    = sa.Column('id', sa.Integer, primary_key=True)
    t_tweet_id            = sa.Column('tweet_id', sa.Integer)
    user_id               = sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
    text                  = sa.Column('text', sa.String(300))
    lang                  = sa.Column('lang', sa.String(10))
    retweet_count         = sa.Column('retweet_count', sa.Integer)
    favorite_count        = sa.Column('favorite_count', sa.Integer)
    source                = sa.Column('source', sa.String(50))
    in_reply_to_status_id = sa.Column('in_reply_to_status_id', sa.Integer)
    coordinates           = sa.Column('coordinates', sadm.JSON())
    place                 = sa.Column('place', sadm.JSON())
    created_at            = sa.Column("created_at", sa.DateTime)

    user                  = relationship("User", back_populates="tweet")

    def __repr__(self):
        return "<Tweet(id={}, tweet_id={})>".format(self.id, self.t_tweet_id)


class Entity(Base):
    """
    Entity Model
    """
    __tablename__ = "entity"

    id                    = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id              = sa.Column('tweet_id', sa.Integer, sa.ForeignKey('tweet.id'))
    user_mentions         = sa.Column('user_mentions', sadm.JSON())
    symbols               = sa.Column('symbols', sadm.JSON() )
    created_at            = sa.Column('created_at', sa.DateTime)

    tweet                 = relationship("Tweet", back_populates="entity")

    def __repr__(self):
        return "<Entity(id={})>".format(self.id)


class EntityUrl(Base):
    """
    Entity Url Model
    """
    __tablename__ = "entity_url"

    id                    = sa.Column('id', sa.Integer, primary_key=True)
    entity_id             = sa.Column('entity_id', sa.Integer, sa.ForeignKey('entity.id'))
    url                   = sa.Column('url', sa.String(100))
    created_at            = sa.Column('created_at', sa.DateTime)

    entity                = relationship("Entity", back_populates="entity_url")

    def __repr__(self):
        return "<Entity_Url(id={}, url={})>".format(self.id, self.url)


class HashTag(Base):
    """
    Entity Hashtag Model
    """
    __tablename__ = "hashtag"

    id                    = sa.Column('id', sa.Integer, primary_key=True)
    entity_id             = sa.Column('entity_id', sa.Integer, sa.ForeignKey('entity.id'))
    hashtag               = sa.Column('hashtag', sa.String(50))
    created_at            = sa.Column('created_at', sa.DateTime)

    entity                = relationship("Entity", back_populates="hashtag")

    def __repr__(self):
        return "<HashTag(id={}, hashtag={})>".format(self.id, self.hashtag)


class User(Base):
    """
    User Model
    """
    __tablename__ = "user"

    id                    = sa.Column('id', sa.Integer, primary_key=True)
    t_user_id             = sa.Column('user_id', sa.Integer)
    name                  = sa.Column('name', sa.String(100))
    screen_name           = sa.Column('screen_name', sa.String(50))
    location              = sa.Column('location', sa.String(50))
    description           = sa.Column('description', sa.String(300))
    followers_count       = sa.Column('favorite_count', sa.Integer)
    friends_count         = sa.Column('friends_count', sa.Integer)
    listed_count          = sa.Column('listed_count', sa.Integer)
    favorites_count       = sa.Column('favorites_count', sa.Integer)
    statuses_count        = sa.Column('statuses_count', sa.Integer)
    created_at            = sa.Column('created_at', sa.DateTime)
    updated_at            = sa.Column('updated_at', sa.DateTime)

    def __repr__(self):
        return "<User(id={}, user_id={}, screen_name={})>".format(self.id, self.t_user_id, self.screen_name)


def main():
    Base.metadata.create_all(bind=ENGINE)


if __name__ == '__main__':
    main()
