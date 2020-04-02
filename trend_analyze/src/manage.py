import sys
import pickle

from controller import Controller
from get_data import GetTweetInfo

sys.path.append("../")
from config import *


class Manage:
    def __init__(self):
        self.gti = GetTweetInfo()
        self.controller = Controller()

    def update_trend_availables(self):
        availables = self.gti.get_trends_available()
        self.controller.insert_trend_availables(availables)

    def store_user_tweet(self, user_id):
        with open('../log/test_tweets.pickle', 'rb') as f:
            tweets = pickle.load(f)

        self.controller.insert_tweet(tweets)


if __name__ == '__main__':
    manage = Manage()
    manage.store_user_tweet(TEST_USER_ID)
