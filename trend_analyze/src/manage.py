import datetime
import time
import logging
import logging.config

from trend_analyze.src.controller import Controller
from trend_analyze.src.get_data_from_api import ApiTwitterGetter
from trend_analyze.src.get_data import TwitterGetter
from trend_analyze.src import table_model
from trend_analyze.config import *


class Manage:
    def __init__(self, is_update: bool = True):
        self.atg = ApiTwitterGetter()
        self.tg = TwitterGetter()
        self.controller = Controller()
        self.model = table_model
        self.is_update = is_update
        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('manage')

    def update_trend_availables(self):
        availables = self.atg.get_trends_available()
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
        for tweets in self.atg.collect_user_tweet(user_id=user_id):
            self.controller.insert_tweet(tweets, is_update=self.is_update)

    def store_tweet_including_trend(self, rank: int = -1, since: int = 1) -> None:
        """
        collect tweet including trend and store it in db
        :param rank: specify trend rank. -1 indicates all trends
        :param since: int since date
        :return: None
        """
        woeids = self.controller.get_woeid()
        trends = self.atg.get_current_trends(woeid=woeids[-1][0])
        trends = trends[0]['trends']

        now = datetime.datetime.now()
        since_date = (now - datetime.timedelta(days=since)).strftime("%Y-%m-%d_00:00:00_JST")
        csvlogger = logging.getLogger("csv")
        start = time.time()

        if rank == -1:
            for trend in trends:
                self.logger.info("Trend volume is {}.".format(trend["tweet_volume"]))

                for tweets in self.atg.collect_tweet_including_target(q=trend['name'],
                                                                      lang='ja',
                                                                      since=since_date):
                    self.controller.insert_tweet(tweets, is_update=self.is_update)

                elapsed_time = time.time() - start
                csvlogger.info("{},{},{}".format(since_date, trend["tweet_volume"], elapsed_time))
                start = time.time()

        else:
            trend = trends[rank - 1]
            self.logger.info("Trend volume is {}.".format(trend["tweet_volume"]))
            for tweets in self.atg.collect_tweet_including_target(q=trend['name'],
                                                                  lang='ja',
                                                                  since=since_date):
                self.controller.insert_tweet(tweets, is_update=self.is_update)

            elapsed_time = time.time() - start
            csvlogger.info("{},{},{}".format(since_date, trend["tweet_volume"], elapsed_time))

        return None

    def store_old_tweet(self, username: str) -> None:
        """
        collect old tweet cannot be collected with official api and store it into db
        :param username: [str] screen name (after '@' character)
        :return: None
        """
        tweets = self.tg.collect_tweet_by_got(username=username)
        self.controller.insert_tweet(tweets)

    def store_users_relation(self, user_id: str) -> None:
        """
        store users relation
        [!!] You must set user id stored in user table
        :param user_id: [str] target user id stored user table
        :return: None
        """
        fr_ids = self.atg.get_friends_id_list(user_id)
        fo_ids = self.atg.get_followed_id_list(user_id)
        self.controller.insert_users_relation(user_id, fr_ids, fo_ids)
        return None
