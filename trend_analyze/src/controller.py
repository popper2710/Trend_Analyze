import time
import re
import sqlalchemy as sa
import logging
import logging.config
from functools import wraps

from .db import session
from . import model
from ..config import *


class Controller:
    # TODO: add function for delete column
    def __init__(self):
        self.session = session

    # ========================================[public method]=========================================
    def logger(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            conf_path = PROJECT_ROOT + "config\logging.ini"

            logging.config.fileConfig(conf_path)
            try:
                print("start this process")
                start = time.time()
                result = func(self, *args, **kwargs)
                elapsed_time = time.time() - start

                msg = f'"{func.__name__}" is succeed. Required time is {elapsed_time}s. '
                logging.info(msg)

                return result
            except Exception as e:
                logging.error(e)

                return None

        return wrapper

    @logger
    def insert_trend_availables(self, availables):
        """
        update table with current trend available location
        :return: None
        """
        items = list()
        append = items.append

        # initialize trend available table
        self.session.execute("DELETE FROM {}".format(model.TrendAvailable.__tablename__))

        for available in availables:
            item = dict()
            item['name'] = available['name']
            item['url'] = available['url']
            item['country'] = available['country']
            item['woeid'] = available['woeid']
            item['countrycode'] = available['countryCode']
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        self.session.execute(model.TrendAvailable.__table__.insert(), items)
        self.session.commit()

    @logger
    def get_woeid(self, countrycode: str = "JP"):
        """
        Returns woeid list correspond countrycode
        :param countrycode: str
        :return:woeids list
        """
        availables = model.TrendAvailable
        woeids = self.session.query(availables.woeid) \
            .filter(availables.countrycode == countrycode) \
            .all()
        return woeids

    @logger
    def insert_tweet(self, tweets: list) -> None:
        """
        insert tweet data from tweepy object
        :param tweets: tweepy object list
        :return None
        """
        items = list()
        append = items.append
        users_id = self.session.query(model.User.t_user_id).all()
        users_id = {user.t_user_id for user in users_id}

        update_users = list()
        u_users_append = update_users.append
        # =========[user data insert process]==========
        for tweet in tweets:
            item = dict()

            # except duplicate and split update user and insert user
            if tweet.user.id_str in users_id:
                if tweet.is_official:
                    u_users_append(tweet.user)
                continue
            else:
                users_id.add(tweet.user.id_str)

            item['user_id'] = tweet.user.id
            item['screen_name'] = tweet.user.screen_name
            item['location'] = tweet.user.location
            item['description'] = tweet.user.description
            item['followers_count'] = tweet.user.followers_count
            item['friends_count'] = tweet.user.friends_count
            item['listed_count'] = tweet.user.listed_count
            item['favorites_count'] = tweet.user.favourites_count
            item['statuses_count'] = tweet.user.statuses_count
            item['created_at'] = tweet.user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        if items:
            self.session.execute(model.User.__table__.insert(), items)
            self.session.commit()
        if update_users:
            self._update_user(update_users)
        # ==================[end]======================

        users_id = self.session.query(model.User.id, model.User.t_user_id).all()
        users_id = {user.t_user_id: user.id for user in users_id}

        t_items, eu_items, eh_items = list(), list(), list()
        t_append, eu_append, eh_append = t_items.append, eu_items.append, eh_items.append

        stored_tweet_id = self.session.query(model.Tweet.t_tweet_id).all()
        stored_tweet_id = {tweet.t_tweet_id for tweet in stored_tweet_id}
        update_tweets = list()
        update_append = update_tweets.append

        for tweet in tweets:
            # =======[build Tweet row data]===========
            t_item = dict()

            # split update tweet and insert tweet
            if tweet.id_str in stored_tweet_id:
                if tweet.is_official:
                    update_append(tweet)

                continue

            t_item['name'] = tweet.user.name
            t_item['tweet_id'] = tweet.id
            t_item['user_id'] = users_id[tweet.user.id_str]
            t_item['text'] = tweet.text
            t_item['lang'] = tweet.lang
            t_item['retweet_count'] = tweet.retweet_count
            t_item['favorite_count'] = tweet.favorite_count
            t_item['source'] = tweet.source
            t_item['in_reply_to_status_id'] = tweet.in_reply_to_status_id
            t_item['coordinates'] = tweet.coordinates
            t_item['place'] = tweet.place
            t_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
            t_append(t_item)
            # ==================[end]=================

            # ========[build Entity row data]=========
            for h in tweet.entities['hashtags']:
                eh_item = dict()
                eh_item['tweet_id'] = tweet.id
                eh_item['hashtag'] = h['text']
                eh_item['start'] = h['indices'][0]
                eh_item['end'] = h['indices'][1]
                eh_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                eh_append(eh_item)

            for u in tweet.entities['urls']:
                eu_item = dict()
                eu_item['tweet_id'] = tweet.id
                eu_item['url'] = u['url']
                eh_item['start'] = u['indices'][0]
                eh_item['end'] = u['indices'][1]
                eu_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                eu_append(eu_item)

            # ==================[end]=================

        if t_items:
            self.session.execute(model.Tweet.__table__.insert(), t_items)
            self.session.commit()
        if update_tweets:
            self._update_tweet(update_tweets)

        if eh_items:
            self.session.execute(model.HashTag.__table__.insert(), eh_items)
        if eu_items:
            self.session.execute(model.EntityUrl.__table__.insert(), eu_items)

        self.session.commit()

    @logger
    def insert_tweet_from_got(self, tweets: list) -> None:
        """
        insert tweet getting with GetOldTweet data from tweepy object
        :param tweets: tweepy object list
        :return None
        """
        items = list()
        append = items.append
        users = self.session.query(model.User.t_user_id).all()
        users_id = {int(user.t_user_id) for user in users}

        # =========[user data insert process]==========
        for tweet in tweets:
            item = dict()

            # except duplicate
            if tweet.author_id in users_id:
                continue
            else:
                users_id.add(tweet.author_id)

            item['user_id'] = tweet.author_id
            item['screen_name'] = tweet.username
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        if items:
            self.session.execute(model.User.__table__.insert(), items)
            self.session.commit()
        # ==================[end]======================

        users_id = self.session.query(model.User.id, model.User.t_user_id).all()
        users_id = {int(user.t_user_id): user.id for user in users_id}

        t_items, eu_items, eh_items = list(), list(), list()
        t_append, eu_append, eh_append = t_items.append, eu_items.append, eh_items.append
        # for extracting hashtag and urls
        url_p = re.compile(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+')
        hashtag_p = re.compile(r'[#＃][Ａ-Ｚａ-ｚA-Za-z一-鿆0-9０-９ぁ-ヶｦ-ﾟー._-]+')
        stored_tweet_id = set(self.session.query(model.Tweet.t_tweet_id).all())

        for tweet in tweets:
            # =======[build Tweet row data]===========
            if tweet.id in stored_tweet_id:
                continue
            else:
                stored_tweet_id.add(tweet.id)

            created_time = tweet.date.strftime('%Y-%m-%d %H:%M:%S')
            t_item = dict()
            t_item['tweet_id'] = tweet.id
            t_item['user_id'] = users_id[tweet.author_id]
            t_item['text'] = tweet.text
            t_item['retweet_count'] = tweet.retweets
            t_item['favorite_count'] = tweet.favorites
            t_item['created_at'] = created_time
            t_append(t_item)
            # ==================[end]=================

            # ========[build Entity row data]=========
            hashtags = hashtag_p.finditer(tweet.text)
            for h in hashtags:
                eh_item = dict()
                eh_item['tweet_id'] = tweet.id
                eh_item['hashtag'] = h.group()[1:]
                eh_item['start'] = h.span()[0]
                eh_item['end'] = h.span()[1]
                eh_item['created_at'] = created_time
                eh_append(eh_item)

            urls = url_p.finditer(tweet.text)
            for u in urls:
                eu_item = dict()
                eu_item['tweet_id'] = tweet.id
                eu_item['url'] = u.group()
                eu_item['start'] = u.span()[0]
                eu_item['end'] = u.span()[1]
                eu_item['created_at'] = created_time
                eu_append(eu_item)

            # ==================[end]=================

        if t_items:
            self.session.execute(model.Tweet.__table__.insert(), t_items)
            self.session.commit()
        if eu_items:
            self.session.execute(model.HashTag.__table__.insert(), eh_items)
        if eh_items:
            self.session.execute(model.EntityUrl.__table__.insert(), eu_items)
        self.session.commit()

    # ========================================[private method]========================================
    def _update_tweet(self, tweets):
        """
        update tweet column with tweet id
        :param tweets: list[tweepy object]
        :return: None
        """
        t = model.Tweet
        stmt = t.__table__.update() \
            .where(t.t_tweet_id == sa.bindparam('_tweet_id')) \
            .values(text=sa.bindparam('_text'),
                    lang=sa.bindparam('_lang'),
                    retweet_count=sa.bindparam('_retweet_count'),
                    favorite_count=sa.bindparam('_favorite_count'),
                    source=sa.bindparam('_source'),
                    in_reply_to_status_id=sa.bindparam('_in_reply_to_status_id'),
                    coordinates=sa.bindparam('_coordinates'),
                    place=sa.bindparam('_place'),
                    created_at=sa.bindparam('_created_at'),
                    )

        t_items = list()
        t_append = t_items.append

        # =======[build Tweet row data]===========
        for tweet in tweets:
            t_item = dict()
            t_item['_tweet_id'] = tweet.id
            t_item['_text'] = tweet.text
            t_item['_lang'] = tweet.lang
            t_item['_retweet_count'] = tweet.retweet_count
            t_item['_favorite_count'] = tweet.favorite_count
            t_item['_source'] = tweet.source
            t_item['_in_reply_to_status_id'] = tweet.in_reply_to_status_id
            t_item['_coordinates'] = tweet.coordinates
            t_item['_place'] = tweet.place
            t_item['_created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')

            t_append(t_item)

        # ==================[end]=================

        self.session.execute(stmt, t_items)
        self.session.commit()

        return None

    def _update_user(self, users):
        """
        update users lacking information with Tweepy object
        :param users: Tweepy User object
        :return None:
        """
        u = model.User
        stmt = u.__table__.update() \
            .where(u.t_user_id == sa.bindparam('_user_id')) \
            .values(name=sa.bindparam('_name'),
                    screen_name=sa.bindparam('_screen_name'),
                    location=sa.bindparam('_location'),
                    description=sa.bindparam('_description'),
                    followers_count=sa.bindparam('_followers_count'),
                    friends_count=sa.bindparam('_friends_count'),
                    listed_count=sa.bindparam('_listed_count'),
                    favorites_count=sa.bindparam('_favorites_count'),
                    statuses_count=sa.bindparam('_statuses_count'),
                    created_at=sa.bindparam('_created_at'),
                    updated_at=sa.bindparam('_updated_at'), )

        items = [{'_user_id': user.id,
                  '_name': user.name,
                  '_screen_name': user.screen_name,
                  '_location': user.location,
                  '_description': user.description,
                  '_followers_count': user.followers_count,
                  '_friends_count': user.friends_count,
                  '_listed_count': user.listed_count,
                  '_favorites_count': user.favourites_count,
                  '_statuses_count': user.statuses_count,
                  '_created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                  '_updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
                  } for user in users]

        self.session.execute(stmt, items)
        self.session.commit()

