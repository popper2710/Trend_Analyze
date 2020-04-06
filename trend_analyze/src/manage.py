import pickle

from .controller import Controller
from .get_data import GetTweetInfo
from . import model
from ..config import *


class Manage:
    def __init__(self):
        self.gti = GetTweetInfo()
        self.controller = Controller()
        self.model = model

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
        tweets = self.gti.collect_tweet(user_id=user_id)
        self.controller.insert_tweet(tweets)

    def store_tweet_including_trend(self, rank: int = -1):
        """
        collect tweet including trend and store it in db
        :param rank:
        :return:
        """
        woeids = self.controller.get_woeid()
        trends = self.gti.get_current_trends(woeid=woeids[-1][0])
        trends = trends[0]['trends']
        if rank == -1:
            for trend in trends:
                tweets = self.gti.collect_tweet_including_target(q=trend['name'], count=1)
                self.controller.insert_tweet(tweets)
            return None
        else:
            trend = trends[rank-1]
            tweets = self.gti.collect_tweet_including_target(q=trend['name'])
            self.controller.insert_tweet(tweets)
            return None

    def store_old_tweet(self, username: str):
        """
        collect old tweet cannot be collected with official api and store it into db
        :param username: str screen name (after '@' character)
        :return: None
        """
        tweets = self.gti.collect_tweet_by_got(username=username)
        self.controller.insert_tweet_from_got(tweets)


