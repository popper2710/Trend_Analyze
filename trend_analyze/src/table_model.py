import sqlalchemy as sa
import sqlalchemy.dialects.mysql as sadm
from sqlalchemy.orm import relationship

from trend_analyze.src.db import Base, ENGINE


class TableTweet(Base):
    """
    Tweet Model
    """
    __tablename__ = "tweet"
    __table_args__ = {'extend_existing': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    t_tweet_id = sa.Column('tweet_id', sa.String(30), unique=True, nullable=False)
    user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, default=-1)
    text = sa.Column('text', sa.String(300), nullable=False, default="")
    lang = sa.Column('lang', sa.String(10))
    retweet_count = sa.Column('retweet_count', sa.Integer)
    favorite_count = sa.Column('favorite_count', sa.Integer)
    source = sa.Column('source', sa.String(50))
    in_reply_to_status_id = sa.Column('in_reply_to_status_id', sa.String(30))
    coordinates = sa.Column('coordinates', sadm.JSON())
    place = sa.Column('place', sadm.JSON())
    created_at = sa.Column("created_at", sa.DateTime)
    updated_at = sa.Column("updated_at", sa.DateTime)

    # children
    user = relationship("TableUser", back_populates="tweet", uselist=False)

    # parent
    hashtag = relationship("TableHashTag", back_populates="tweet", cascade="all, delete-orphan")
    entity_url = relationship("TableEntityUrl", back_populates="tweet", cascade="all, delete-orphan")

    def __repr__(self):
        return "<TableTweet(id={}, tweet_id={})>".format(self.id, self.t_tweet_id)


class TableEntityUrl(Base):
    """
    Entity Url Model
    """
    __tablename__ = "entity_url"
    __table_args__ = {'extend_existing': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id = sa.Column('tweet_id', sa.String(30), sa.ForeignKey("tweet.tweet_id", ondelete="CASCADE"), nullable=False)
    url = sa.Column('url', sa.String(150), nullable=False)
    start = sa.Column('start', sa.Integer, nullable=False, default=-1)
    end = sa.Column('end', sa.Integer, nullable=False, default=-1)
    created_at = sa.Column('created_at', sa.DateTime, nullable=False)

    # children
    tweet = relationship("TableTweet", back_populates="entity_url")

    def __repr__(self):
        return "<TableEntity_Url(id={}, url={})>".format(self.id, self.url)


class TableHashTag(Base):
    """
    Entity Hashtag Model
    """
    __tablename__ = "hashtag"
    __table_args__ = {'extend_existing': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    tweet_id = sa.Column('tweet_id', sa.String(30), sa.ForeignKey("tweet.tweet_id", ondelete="CASCADE"), nullable=False)
    hashtag = sa.Column('hashtag', sa.String(150), nullable=False)
    start = sa.Column('start', sa.Integer, nullable=False)
    end = sa.Column('end', sa.Integer, nullable=False)
    created_at = sa.Column('created_at', sa.DateTime, nullable=False)

    # children
    tweet = relationship("TableTweet", back_populates="hashtag")

    def __repr__(self):
        return "<TableHashTag(id={}, hashtag={})>".format(self.id, self.hashtag)


class TableUser(Base):
    """
    User Model
    """
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    t_user_id = sa.Column('user_id', sa.String(30), unique=True, nullable=False)
    name = sa.Column('name', sa.String(100))
    screen_name = sa.Column('screen_name', sa.String(50))
    location = sa.Column('location', sa.String(50))
    description = sa.Column('description', sa.String(300))
    followers_count = sa.Column('followers_count', sa.Integer)
    friends_count = sa.Column('friends_count', sa.Integer)
    listed_count = sa.Column('listed_count', sa.Integer)
    favorites_count = sa.Column('favorites_count', sa.Integer)
    statuses_count = sa.Column('statuses_count', sa.Integer)
    created_at = sa.Column('created_at', sa.DateTime)
    updated_at = sa.Column('updated_at', sa.DateTime)

    # parent
    tweet = relationship("TableTweet", back_populates="user", cascade='all, delete-orphan', lazy="select")
    users_relation = relationship("TableUsersRelation", back_populates="user", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return "<TableUser(id={}, user_id={}, screen_name={})>".format(self.id, self.t_user_id, self.screen_name)


class TableTrendAvailable(Base):
    """
    Trend Available location Model
    """

    __tablename__ = "trend_available"
    __table_args__ = {'extend_existing': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String(20))
    url = sa.Column('url', sa.String(50))
    country = sa.Column('country', sa.String(50))
    woeid = sa.Column('woeid', sa.Integer)
    countrycode = sa.Column('countrycode', sa.String(10))
    updated_at = sa.Column('updated_at', sa.DateTime)

    def __repr__(self):
        return "<TableTrendAvailable(id={}, name={})>".format(self.id, self.name)


class TableUsersRelation(Base):
    """
    Users relationship model
    """
    __tablename__ = "users_relation"
    __table_args__ = {'extend_existing': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    user_id = sa.Column('user_id', sa.String(30), sa.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    target_id = sa.Column('target_id', sa.String(30), nullable=False)
    relation_id = sa.Column('relation_id', sa.Integer, nullable=False, default=-1)
    updated_at = sa.Column('updated_at', sa.DateTime)

    user = relationship("TableUser", back_populates="users_relation")

    def __repr__(self):
        return "<TableUsersRelation(id={}, user={}, target={}, relation={})>".format(self.id,
                                                                                     self.user_id,
                                                                                     self.target_id,
                                                                                     self.relation_id)


def create_database():
    Base.metadata.create_all(bind=ENGINE)
