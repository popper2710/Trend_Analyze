import pickle
import datetime

from .controller import Controller
from .get_data import GetTweetInfo
from . import model
from ..config import *


class Manage:
    def __init__(self, is_update: bool = True):
        self.gti = GetTweetInfo()
        self.controller = Controller()
        self.model = model
        self.is_update = is_update

    def update_trend_availables(self):
        availables = self.gti.get_trends_available()
        self.controller.insert_trend_availables(availables)

    def create_database(self):
        self.model.create_database()

    def store_user_tweet(self, user_id: int):
        """
        collect tweet written by specify user and store it in db
        :param user_id: int
        :return: None
        """
        for tweets in self.gti.collect_user_tweet(user_id=user_id):
            self.controller.insert_tweet(tweets, is_update=self.is_update)

    def store_tweet_including_trend(self, rank: int = -1, since: int = 1) -> None:
        """
        collect tweet including trend and store it in db
        :param rank: specify trend rank. -1 indicates all trends
        :param since: int since date
        :return: None
        """
        woeids = self.controller.get_woeid()
        trends = self.gti.get_current_trends(woeid=woeids[-1][0])
        trends = trends[0]['trends']

        now = datetime.datetime.now()
        since_date = (now - datetime.timedelta(days=since)).strftime("%Y-%m-%d_00:00:00_JST")

        if rank == -1:
            for trend in trends:
                for tweets in self.gti.collect_tweet_including_target(q=trend['name'],
                                                                      lang='ja',
                                                                      since=since_date):
                    self.controller.insert_tweet(tweets, is_update=self.is_update)

            return None
        else:
            trend = trends[rank - 1]
            for tweets in self.gti.collect_tweet_including_target(q=trend['name'],
                                                                  lang='ja',
                                                                  since=since_date):
                self.controller.insert_tweet(tweets, is_update=self.is_update)

            return None

    def store_old_tweet(self, username: str) -> None:
        """
        collect old tweet cannot be collected with official api and store it into db
        :param username: str screen name (after '@' character)
        :return: None
        """
        tweets = self.gti.collect_tweet_by_got(username=username)
        self.controller.insert_tweet_from_got(tweets)
