import datetime
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

        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('manage')

    def update_trend_availables(self):
        availables = self.atf.fetch_trends_available()
        self.controller.insert_trend_availables(availables)

    def create_database(self):
        self.model.create_database()

    def store_user_tweet(self, user_id: int):
        """
        collect tweet written by specify user and store it in db
        :param user_id:
        :type user_id: int
        :return: None
        """
        for tweets in self.atf.fetch_user_tweet(user_id=user_id):
            self.controller.insert_tweet(tweets, is_update=self.is_update)

    def store_user_tweet_n(self, username: str) -> None:
        """
        store user tweet without using official api
        :param username: screen name (after '@' character)
        :type  username: str
        :return: None
        """
        tweets = self.tf.fetch_tweet(username=username)
        self.controller.insert_tweet(tweets)

    def store_tweet_including_trend(self, rank: int = -1, since: int = 1) -> None:
        """
        store tweet including trend word
        :param rank: specify trend rank. -1 indicates all trends
        :type rank: int
        :param since: since date
        :type since:int
        :return: None
        """
        woeids = self.controller.get_woeid()
        trends = self.atf.fetch_current_trends(woeid=woeids[-1][0])
        trends = trends[0]['trends']

        now = datetime.datetime.now()
        since_date = (now - datetime.timedelta(days=since)).strftime("%Y-%m-%d_00:00:00_JST")
        csvlogger = logging.getLogger("csv")
        start = time.time()

        if rank == -1:
            for trend in trends:
                self.logger.info("Trend volume is {}.".format(trend["tweet_volume"]))

                for tweets in self.atf.fetch_tweet_including_target(q=trend['name'],
                                                                    lang='ja',
                                                                    since=since_date):
                    self.controller.insert_tweet(tweets, is_update=self.is_update)

                elapsed_time = time.time() - start
                csvlogger.info("{},{},{}".format(since_date, trend["tweet_volume"], elapsed_time))
                start = time.time()

        else:
            trend = trends[rank - 1]
            self.logger.info("Trend volume is {}.".format(trend["tweet_volume"]))
            for tweets in self.atf.fetch_tweet_including_target(q=trend['name'],
                                                                lang='ja',
                                                                since=since_date):
                self.controller.insert_tweet(tweets, is_update=self.is_update)

            elapsed_time = time.time() - start
            csvlogger.info("{},{},{}".format(since_date, trend["tweet_volume"], elapsed_time))

        return None

    def store_user_tweet_n(self, username: str) -> None:
        """
        collect old tweet cannot be collected with official api and store it into db
        :param username: screen name (after '@' character)
        :type  username: str
        :return: None
        """
        tweets = self.tf.fetch_tweet(username=username)
        self.controller.insert_tweet(tweets)

    def store_tweet_including_word(self, word: str, since: int = 1):
        """
        store tweet including specifying word
        :param word: word included collecting tweet
        :param since: since date (yesterday => 1 a week ago => 7)
        :return: None
        """
        now = datetime.datetime.now()
        since_date = (now - datetime.timedelta(days=since)).strftime("%Y-%m-%d_00:00:00_JST")
        for tweets in self.atf.fetch_tweet_including_target(q=word,
                                                            lang='ja',
                                                            since=since_date):
            self.controller.insert_tweet(tweets, is_update=self.is_update)
        return None

    def store_tweet_including_word_n(self, word: str, max_tweet: int = 0, since: int = 0, until: int = 0):
        """
        store tweet including specifying word without using api
        :param word: word included collecting tweet
        :param max_tweet: max tweet count
        :param since: since date (yesterday => 1, a week ago => 7)
        :param until: until date (yesterday => 1, a week ago => 7)
        :return: None
        """
        tweets = self.tf.fetch_tweet(q=word, max_tweet=max_tweet, since=since, until= until)
        self.controller.insert_tweet(tweets, is_update=self.is_update)
        return None

    def store_users_relation(self, user_id: str) -> None:
        """
        store users relation
        [!!] You must set user id stored in user table
        :param user_id: target user id stored user table
        :type user_id: str
        :return: None
        """
        fr_ids = self.atf.fetch_friends_id_list(user_id)
        fo_ids = self.atf.fetch_followed_id_list(user_id)
        self.controller.insert_users_relation(user_id, fr_ids, fo_ids)
        return None

    def store_users_relation_n(self, username: str) -> None:
        """
        store users relation without using api
        [!!] You must set user id stored in user table
        :param username: username
        :type username: str
        :return:
        """
        user_id = session.query(table_model.TableUser.t_user_id).first()
        fr_ids = self.atf.fetch_friends_id_list(username)
        fo_ids = self.atf.fetch_followed_id_list(username)
        self.controller.insert_users_relation(user_id, fr_ids, fo_ids)
        return None

    def upgrade_user(self, user):
        """
        upgrade incomplete user records
        :param user: username or user id
        :type user: str
        :return:
        """
        user = self.atf.fetch_user_info(user)
        self.controller.update_user(user)
        return None

    def upgrade_user_n(self, name: str):
        """
        upgrade incomplete user records from name without using api
        :param name: username
        :type name: str
        :return:
        """
        user = self.tf.fetch_user_info_from_name(name)
        self.controller.update_user([user])
        return None
