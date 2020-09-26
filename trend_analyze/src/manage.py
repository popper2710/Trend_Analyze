from datetime import datetime, timedelta
import time
import logging
import logging.config

from trend_analyze.src.controller import Controller
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher
from trend_analyze.src.fetch_data import TwitterFetcher

from trend_analyze.src.db import session
from trend_analyze.src import table_model
from trend_analyze.config import *


class Manage:
    """
    This class supervises other classes. Suffix "_n" to method name estimates that it doesn't use twitter api.
    If you use Trend_Analyze, it recommends you to use only this class.
    """

    def __init__(self, is_update: bool = True):
        self.atf = ApiTwitterFetcher()
        self.tf = TwitterFetcher()
        self.controller = Controller()
        self.model = table_model
        self.model.create_database()

        self.is_update = is_update

        logging.config.dictConfig(LOGGING_DICT_CONFIG)
        self.logger = logging.getLogger('manage')

    def update_trend_availables(self):
        """
        update trend availables table to current one
        :return:
        """
        availables = self.atf.fetch_trends_available()
        self.controller.insert_trend_availables(availables)

    def store_user_tweet(self, user_id: str, max_tweet: int = TWEET_FETCH_LIMIT):
        """
        collect tweet written by specify user and store it in db
        :param user_id:
        :type user_id: str
        :param max_tweet: maximum number of tweets to fetch
        :type max_tweet: int
        :return: None
        """
        for tweets in self.atf.fetch_user_tweet(user_id=user_id, max_tweet=max_tweet):
            self.controller.insert_tweet(tweets, is_update=self.is_update)

    def store_user_tweet_n(self, username: str) -> None:
        """
        collect old tweet cannot be collected with official api and store it into db
        :param username: screen name (after '@' character)
        :type  username: str
        :return: None
        """
        tweets = self.tf.fetch_tweet(username=username)
        self.controller.insert_tweet(tweets)

    def store_tweet_including_trend(self, rank: int = -1, since: int = 1, max_tweet: int = TWEET_FETCH_LIMIT,
                                    is_RT: bool = False) -> None:
        """
        store tweet including trend word
        :param rank: specify trend rank. -1 indicates all trends
        :type rank: int
        :param since: since date
        :type since:int
        :param max_tweet: maximum number of tweets to fetch
        :type max_tweet: int
        :param is_RT: if it's true, you can store retweet including trend
        :type is_RT: bool
        :return: None
        """
        self.update_trend_availables()
        woeids = self.controller.get_woeid()
        trends = self.atf.fetch_current_trends(woeid=woeids[-1][0])
        trends = trends[0]['trends']

        now = datetime.now()
        since_date = (now - timedelta(days=since)).strftime("%Y-%m-%d_00:00:00_JST")
        csvlogger = logging.getLogger("csv")
        start = time.time()

        if rank == -1:
            remaining_tweet_num = max_tweet
            for trend in trends:
                self.logger.info("Trend volume is {}.".format(trend["tweet_volume"]))

                for tweets in self.atf.fetch_tweet_including_target(q=trend['name'],
                                                                    is_RT=is_RT,
                                                                    is_name=False,
                                                                    lang='ja',
                                                                    since=since_date,
                                                                    max_tweet=remaining_tweet_num):
                    remaining_tweet_num -= len(tweets)
                    self.controller.insert_tweet(tweets, is_update=self.is_update)

                elapsed_time = time.time() - start
                csvlogger.info("{},{},{}".format(since_date, trend["tweet_volume"], elapsed_time))
                start = time.time()

        else:
            trend = trends[rank - 1]
            self.logger.info("Trend volume is {}.".format(trend["tweet_volume"]))
            for tweets in self.atf.fetch_tweet_including_target(q=trend['name'],
                                                                is_RT=is_RT,
                                                                is_name=False,
                                                                lang='ja',
                                                                since=since_date,
                                                                max_tweet=max_tweet):
                self.controller.insert_tweet(tweets, is_update=self.is_update)

            elapsed_time = time.time() - start
            csvlogger.info("{},{},{}".format(since_date, trend["tweet_volume"], elapsed_time))

        return None

    def store_tweet_including_word(self, word: str, since: int = 1, max_tweet: int = TWEET_FETCH_LIMIT,
                                   is_RT: bool = True, is_name: bool = True):
        """
        store tweet including specifying word
        :param word: word included collecting tweet
        :type word: str
        :param max_tweet: max tweet count
        :type max_tweet: int
        :param since: since date (yesterday => 1 a week ago => 7)
        :type since: int
        :param is_RT: if it's true, you can store retweet including keyword
        :type is_RT: bool
        :param is_name: if it's true, you can store the tweet posted by the user having username including trend
        :return: None
        """
        now = datetime.now()
        since_date = (now - timedelta(days=since)).strftime("%Y-%m-%d_00:00:00_JST")
        for tweets in self.atf.fetch_tweet_including_target(q=word,
                                                            is_RT=is_RT,
                                                            is_name=is_name,
                                                            lang='ja',
                                                            since=since_date,
                                                            max_tweet=max_tweet
                                                            ):
            self.controller.insert_tweet(tweets, is_update=self.is_update)
        return None

    def store_tweet_including_word_n(self, word: str, max_tweet: int = TWEET_FETCH_LIMIT, since: int = 0,
                                     until: int = 0):
        """
        store tweet including specifying word without using api
        :param word: word included collecting tweet
        :param max_tweet: max tweet count
        :param since: since date (yesterday => 1, a week ago => 7)
        :param until: until date (yesterday => 1, a week ago => 7)
        :return: None
        """
        tweets = self.tf.fetch_tweet(q=word, max_tweet=max_tweet, since=since, until=until)
        self.controller.insert_tweet(tweets, is_update=self.is_update)
        return None

    def store_users_relation(self, user_id: str) -> None:
        """
        store users relation
        :param user_id: target user id stored user table
        :type user_id: str
        :return: None
        """
        if not self.controller.is_exist_user(user_id=user_id):
            self.store_user(user_id=user_id)
        fr_ids = self.atf.fetch_friends_id_list(user_id)
        fo_ids = self.atf.fetch_followed_id_list(user_id)
        self.controller.insert_users_relation(user_id, fr_ids, fo_ids)
        return None

    def store_users_relation_n(self, username: str) -> None:
        """
        store users relation without using api
        :param username: username
        :type username: str
        :return:
        """
        user_id = self.tf.name_to_id(username)
        if not self.controller.is_exist_user(user_id=user_id):
            self.store_user(user_id=user_id)
        fr_ids = self.tf.fetch_follower_list(username)
        fo_ids = self.tf.fetch_following_list(username)
        self.controller.insert_users_relation(user_id, fr_ids, fo_ids)
        return None

    def store_user(self, user_id: str) -> bool:
        """
        If user having given user id doesn't exist in db, fetch user information and store it in db.
        :param user_id: target user id
        :return: bool (if target user already exists, it returns False)
        """
        if self.controller.is_exist_user(user_id):
            return False
        else:
            user = self.atf.fetch_user_info(user=user_id)
            self.controller.insert_user([user])
            return True

    def upgrade_user(self, user: str):
        """
        upgrade incomplete user records
        :param user: username or user id
        :type user: str
        :return:
        """
        user = self.atf.fetch_user_info(user)
        self.controller.update_user([user])
        return None

    def upgrade_user_n(self, username: str):
        """
        upgrade incomplete user records from name without using api
        :param username: username
        :type username: str
        :return:
        """
        user = self.tf.fetch_user_info_from_name(username)
        self.controller.update_user([user])
        return None

    def get_limit_status(self):
        """
        return twitter api rate limit statuses
        :return: dict
        """
        return self.atf.fetch_limit_status()
