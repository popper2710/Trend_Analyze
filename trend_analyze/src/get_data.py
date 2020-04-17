import logging
import logging.config
import datetime
import time

import GetOldTweets3 as Got
from twitterscraper.query import query_user_info

from trend_analyze.config import *


class TwitterGetter:
    """
    TwitterGetter can collect data without Api's limitation. But it may collect uncomplete information or can only
    collect parts of data. If you want to collect complete data, use ApiTwitterGetter instead of ApiTwitterGetter
    """
    def __init__(self):
        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('get_data')

    def get_user_info_from_name(self, username: str):
        """
        get uncomplete user information with username
        :type username: str
        :param username: screen name except first '@'
        :return: query
        """
        try:
            user_info = query_user_info(username)
        except Exception as e:
            self.logger.error(e)
            user_info = None

        return user_info

    def collect_tweet_by_got(self, username: str = "", max_tweet: int = 0, q: str = ""):
        """
        collect tweets with GetOldPython3
        [!!] this method may take a lot of time, if you don't specify max tweet count.
        :param username: screen name except '@'
        :type username: str
        :param max_tweet:  max tweet count
        :type max_tweet: int
        :param q: search word
        :type q: str
        :return: list[got object]:
        """
        try:
            tc = Got.manager.TweetCriteria()

            if username:
                tc.setUsername(username)

            if max_tweet:
                tc.setMaxTweets(max_tweet)

            if q:
                tc.setQuerySearch(q)

            tmp = Got.manager.TweetManager.getTweets(tc)
            g_tweets = list()
            g_append = g_tweets.append
            for g_tweet in tmp:
                g_tweet.is_official = False
                g_append(g_tweet)

            return g_tweets

        except Exception as e:
            self.logger.error(e)
            return None
