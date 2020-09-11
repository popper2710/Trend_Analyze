import time
import sys
import logging
import logging.config
from functools import wraps

import sqlalchemy as sa

from trend_analyze.src.db import session
from trend_analyze.src import table_model
from trend_analyze.config import *


class Controller:
    def __init__(self):
        self.session = session

    # ========================================[public method]=========================================
    def logger(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):

            logging.config.dictConfig(LOGGING_DICT_CONFIG)
            logger = logging.getLogger('controller')
            try:
                start = time.time()

                result = func(self, *args, **kwargs)
                elapsed_time = time.time() - start

                msg = f'"{func.__name__}" is succeed. Required time was {elapsed_time}s. '
                logger.info(msg)

                return result

            except Exception as e:
                logging.error(e)
                sys.exit(-1)

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
        self.session.execute("DELETE FROM {}".format(table_model.TableTrendAvailable.__tablename__))

        for available in availables:
            item = dict()
            item['name'] = available['name']
            item['url'] = available['url']
            item['country'] = available['country']
            item['woeid'] = available['woeid']
            item['countrycode'] = available['countryCode']
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        self.session.execute(table_model.TableTrendAvailable.__table__.insert(), items)
        self.session.commit()

    @logger
    def get_woeid(self, countrycode: str = "JP"):
        """
        Returns woeid list correspond countrycode
        :param countrycode:
        :type countrycode: str
        :return:woeids [list]
        """
        availables = table_model.TableTrendAvailable
        woeids = self.session.query(availables.woeid) \
            .filter(availables.countrycode == countrycode) \
            .all()
        return woeids

    @logger
    def insert_tweet(self, tweets: list, is_update: bool = True) -> None:
        """
        insert tweet data from common tweet model
        [!!] If you gives Tweet objects having same tweet_id, it raises Duplicate Error.
        :param is_update: flag for updating already existing records. you can improve speed if you set False
        :type is_update: bool
        :param tweets:
        :type tweets: list[Tweet]
        :return None
        """
        stored_user_ids = self.session.query(table_model.TableUser.t_user_id).all()
        stored_user_ids = {user.t_user_id for user in stored_user_ids}

        insert_users = list()
        update_users = list()
        i_users_append = insert_users.append
        u_users_append = update_users.append
        # for except duplicate user record
        update_user_ids = set()
        # =========[user data insert process]==========
        for tweet in tweets:
            # except duplicate and split update user and insert user
            check_user = tweet.user
            check_user_id = check_user.user_id

            # extract update user
            if check_user_id in stored_user_ids:
                if check_user_id in update_user_ids:
                    continue
                if tweet.is_official:
                    u_users_append(check_user)
                    update_user_ids.add(check_user_id)
                continue
            else:
                stored_user_ids.add(check_user_id)
                i_users_append(check_user)

        if insert_users:
            self.insert_user(insert_users)
        if update_users and is_update:
            self.update_user(update_users)
        # ==================[end]======================

        stored_user_ids = self.session.query(table_model.TableUser.id, table_model.TableUser.t_user_id).all()
        stored_user_ids = {user.t_user_id: user.id for user in stored_user_ids}

        t_items, eu_items, eh_items = list(), list(), list()
        t_append, eu_append, eh_append = t_items.append, eu_items.append, eh_items.append

        # NOTE: source column is used for evaluating whether this tweet have been updated by official api.
        stored_tweet = self.session.query(table_model.TableTweet.t_tweet_id, table_model.TableTweet.source).all()
        stored_tweet = {tweet.t_tweet_id: tweet.source for tweet in stored_tweet}

        update_tweets = list()
        update_append = update_tweets.append

        for tweet in tweets:
            # =======[build Tweet row data]===========
            t_item = dict()

            # split update tweet and insert tweet
            if tweet.tweet_id in stored_tweet:
                if stored_tweet[tweet.tweet_id] == "" and tweet.is_official:
                    update_append(tweet)
                continue

            t_item['name'] = tweet.user.name
            t_item['tweet_id'] = tweet.tweet_id
            t_item['user_id'] = stored_user_ids[tweet.user.user_id]
            t_item['text'] = tweet.text
            t_item['lang'] = tweet.lang
            t_item['retweet_count'] = tweet.retweet_count
            t_item['favorite_count'] = tweet.favorite_count
            t_item['source'] = tweet.source
            t_item['in_reply_to_status_id'] = tweet.in_reply_to_status_id
            t_item['coordinates'] = tweet.coordinates
            t_item['place'] = tweet.place
            t_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
            t_item['updated_at'] = tweet.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            t_append(t_item)
            # ==================[end]=================

            # ========[build Entity row data]=========
            for h in tweet.hashtags:
                eh_item = dict()
                eh_item['tweet_id'] = tweet.tweet_id
                eh_item['hashtag'] = h.hashtag
                eh_item['start'] = h.start
                eh_item['end'] = h.end
                eh_item['created_at'] = h.created_at.strftime('%Y-%m-%d %H:%M:%S')
                eh_append(eh_item)

            for u in tweet.urls:
                eu_item = dict()
                eu_item['tweet_id'] = tweet.tweet_id
                eu_item['url'] = u.url
                eu_item['start'] = u.start
                eu_item['end'] = u.end
                eu_item['created_at'] = u.created_at.strftime('%Y-%m-%d %H:%M:%S')
                eu_append(eu_item)
            # ==================[end]=================

        if t_items:
            self.session.execute(table_model.TableTweet.__table__.insert(), t_items)
            self.session.commit()
        if update_tweets and is_update:
            self._update_tweet(update_tweets)

        if eh_items:
            self.session.execute(table_model.TableHashTag.__table__.insert(), eh_items)
        if eu_items:
            self.session.execute(table_model.TableEntityUrl.__table__.insert(), eu_items)

        self.session.commit()

    @logger
    def insert_user(self, users: list):
        """
        insert user from common users model
        [!!] if you gives User objects having same user_id, it raises Duplicate Error.
        :param users:
        :return:
        """
        items = [{'user_id': user.user_id,
                  'name': user.name,
                  'screen_name': user.screen_name,
                  'location': user.location,
                  'description': user.description,
                  'followers_count': user.followers_count,
                  'friends_count': user.following_count,
                  'listed_count': user.listed_count,
                  'favorites_count': user.favorites_count,
                  'statuses_count': user.statuses_count,
                  'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                  'updated_at': user.updated_at
                  } for user in users]
        self.session.execute(table_model.TableUser.__table__.insert(), items)
        self.session.commit()

    @logger
    def insert_users_relation(self, user_id: str, friend_ids: list, followed_ids: list):
        """
        extract user relations and insert them
        [!!] Don't set incomplete id list otherwise this function can't work well.
        :param user_id: target user id
        :type user_id: str
        :param friend_ids: ids that target user is following users
        :type friend_ids: list[str]
        :param followed_ids: ids that target user is followed users
        :type followed_ids: list[str]
        :return: None
        """
        fr_ids = set(friend_ids)
        fo_ids = set(followed_ids)

        bidi_ids = fr_ids & fo_ids
        only_fr_ids = fr_ids.difference(fo_ids)
        only_fo_ids = fo_ids.difference(fr_ids)

        # delete user relation not to generate duplicate records
        del_relation = self.session.query(table_model.TableUsersRelation.target_id) \
            .filter(table_model.TableUsersRelation.user_id == user_id)
        self.session.delete(del_relation)

        updated_date = time.strftime('%Y-%m-%d %H:%M:%S')

        def item_builder(x, y):
            return [{"user_id": user_id,
                     "target_id": i,
                     "relation": y,
                     "updated_at": updated_date
                     } for i in x]

        items = list()
        items.extend(item_builder(only_fr_ids, 0))
        items.extend(item_builder(only_fo_ids, 1))
        items.extend(item_builder(bidi_ids, 2))

        self.session.execute(table_model.TableUsersRelation.__table__.insert(), items)
        self.session.commit()

    @logger
    def execute_sql(self, sql: str):
        """
        [!!] To use this too much may make module coupling strong.
        execute sql statement given as argument
        :param sql: sql statement for execute
        :type sql: str
        :return: Sqlalchemy Result object
        """
        result = self.session.execute(sql)
        logging.info(f"Execute query: '{sql}'")
        self.session.commit()
        return result

    def update_user(self, users):
        """
        update users lacking information with Tweepy object
        :param users:
        :type users: list[User]
        :return None:
        """
        u = table_model.TableUser
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

        items = [{'_user_id': user.user_id,
                  '_name': user.name,
                  '_screen_name': user.screen_name,
                  '_location': user.location,
                  '_description': user.description,
                  '_followers_count': user.followers_count,
                  '_friends_count': user.following_count,
                  '_listed_count': user.listed_count,
                  '_favorites_count': user.favorites_count,
                  '_statuses_count': user.statuses_count,
                  '_created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                  '_updated_at': user.updated_at
                  } for user in users]

        self.session.execute(stmt, items)
        self.session.commit()

    # ========================================[private method]========================================
    def _update_tweet(self, tweets):
        """
        update tweet column with tweet id
        :param tweets:
        :type tweets: list[Tweet]
        :return: None
        """
        t = table_model.TableTweet
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

        # =======[build Tweet row data]===========
        t_items = [{
            '_tweet_id': tweet.tweet_id,
            '_text': tweet.text,
            '_lang': tweet.lang,
            '_retweet_count': tweet.retweet_count,
            '_favorite_count': tweet.favorite_count,
            '_source': tweet.source,
            '_in_reply_to_status_id': tweet.in_reply_to_status_id,
            '_coordinates': tweet.coordinates,
            '_place': tweet.place,
            '_created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            for tweet in tweets]

        # ==================[end]=================

        self.session.execute(stmt, t_items)
        self.session.commit()

        return None
