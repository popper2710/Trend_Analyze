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

    def store_user_tweet(self, user_id):
        """
        get tweet written by specify user and insert it into db
        :param user_id: int
        :return: None
        """
        tweets = self.gti.collect_tweet(user_id=user_id)
        self.controller.insert_tweet(tweets)

