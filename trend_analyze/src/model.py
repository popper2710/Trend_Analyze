import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sadm
from sqlalchemy.orm import relationship

from db import Base, ENGINE


class Tweet(Base):
    """
    Tweet Model
    """
    __tablename__ = "tweet"

    id = sa.Column('id', sa.Integer, primary_key=True)
    t_tweet_id = sa.Column('tweet_id', sa.String(30), unique=True, nullable=False)
    user_id = sa.Column('user_id', sa.Integer, nullable=False)
    text = sa.Column('text', sa.String(300), nullable=False)
    lang = sa.Column('lang', sa.String(10))
    retweet_count = sa.Column('retweet_count', sa.Integer)
    favorite_count = sa.Column('favorite_count', sa.Integer)
    source = sa.Column('source', sa.String(50))
    in_reply_to_status_id = sa.Column('in_reply_to_status_id', sa.Integer)
    coordinates = sa.Column('coordinates', sadm.JSON())
    place = sa.Column('place', sadm.JSON())
    created_at = sa.Column("created_at", sa.DateTime)

    # children
    user = relationship("User", back_populates="tweet")

    # parent
    hashtag = relationship("HashTag", back_populates="tweet")
    entity_url = relationship("EntityUrl", back_populates="tweet")

    def __repr__(self):
        return "<Tweet(id={}, tweet_id={})>".format(self.id, self.t_tweet_id)


class EntityUrl(Base):
    """
    Entity Url Model
    """
    __tablename__ = "entity_url"

    id = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id = sa.Column('tweet_id', sa.String(30), nullable=False)
    url = sa.Column('url', sa.String(100), nullable=False)
    start = sa.Column('start', sa.Integer, nullable=False)
    end = sa.Column('end', sa.Integer, nullable=False)
    created_at = sa.Column('created_at', sa.DateTime, nullable=False)

    # children
    tweet = relationship("Tweet", back_populates="entity_url")

    def __repr__(self):
        return "<Entity_Url(id={}, url={})>".format(self.id, self.url)


class HashTag(Base):
    """
    Entity Hashtag Model
    """
    __tablename__ = "hashtag"

    id = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id = sa.Column('tweet_id', sa.String(30), nullable=False)
    hashtag = sa.Column('hashtag', sa.String(50), nullable=False)
    start = sa.Column('start', sa.Integer, nullable=False)
    end = sa.Column('end', sa.Integer, nullable=False)
    created_at = sa.Column('created_at', sa.DateTime, nullable=False)

    # children
    tweet = relationship("Tweet", back_populates="hashtag")

    def __repr__(self):
        return "<HashTag(id={}, hashtag={})>".format(self.id, self.hashtag)


class User(Base):
    """
    User Model
    """
    __tablename__ = "user"

    id = sa.Column('id', sa.Integer, primary_key=True)
    t_user_id = sa.Column('user_id', sa.String(30), unique=True, nullable=False)
    name = sa.Column('name', sa.String(100))
    screen_name = sa.Column('screen_name', sa.String(50))
    location = sa.Column('location', sa.String(50))
    description = sa.Column('description', sa.String(300))
    followers_count = sa.Column('favorite_count', sa.Integer)
    friends_count = sa.Column('friends_count', sa.Integer)
    listed_count = sa.Column('listed_count', sa.Integer)
    favorites_count = sa.Column('favorites_count', sa.Integer)
    statuses_count = sa.Column('statuses_count', sa.Integer)
    created_at = sa.Column('created_at', sa.DateTime)
    updated_at = sa.Column('updated_at', sa.DateTime)

    # parent
    tweet = relationship("Tweet", back_populates="user")

    def __repr__(self):
        return "<User(id={}, user_id={}, screen_name={})>".format(self.id, self.t_user_id, self.screen_name)


class TrendAvailable(Base):
    """
    Trend Available location Model
    """

    __tablename__ = "trend_available"

    id = sa.Column('id', sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String(20))
    url = sa.Column('url', sa.String(50))
    country = sa.Column('country', sa.String(50))
    woeid = sa.Column('woeid', sa.Integer)
    countrycode = sa.Column('countrycode', sa.String(10))
    updated_at = sa.Column('updated_at', sa.DateTime)

    def __repr__(self):
        return "<TrendAvailable(id={}, name={})>".format(self.id, self.name)


def main():
    Base.metadata.create_all(bind=ENGINE)


if __name__ == '__main__':
    main()
