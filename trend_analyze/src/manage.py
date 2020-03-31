import sys

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
        self.controller(availables)

    def store_user_tweet(self, user_id):
        g_tweets = self.gti.collect_tweets_by_got(TEST_USERNAME, max_tweet=200)
        self.controller.insert_tweet_from_got(g_tweets)


if __name__ == '__main__':
    manage = Manage()
    manage.store_user_tweet(TEST_USERNAME)

