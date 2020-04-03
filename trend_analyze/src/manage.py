import pickle

from .controller import Controller
from .get_data import GetTweetInfo
from .model import main
from ..config import *


class Manage:
    def __init__(self):
        self.gti = GetTweetInfo()
        self.controller = Controller()

    def update_trend_availables(self):
        availables = self.gti.get_trends_available()
        self.controller.insert_trend_availables(availables)

    def store_user_tweet(self, user_id):
        self.gti.get_trends_available()
        with open(PROJECT_ROOT + '/log/test_tweets.pickle', 'rb') as f:
            tweets = pickle.load(f)
        self.controller.insert_tweet(tweets)

