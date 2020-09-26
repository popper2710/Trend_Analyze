import logging
import logging.config
import datetime

import GetOldTweets3 as Got
import twitterscraper
from typing import List

from trend_analyze.src.convert_to_model import ConvertTM
from trend_analyze.src.scraping_tweet import TwitterScraper
from trend_analyze.config import *
from trend_analyze.src.model import *


class TwitterFetcher:
    """
    TwitterFetcher can collect data without Api's limitation. But it may collect incomplete information or can only
    collect parts of data. If you want to collect complete data, use ApiTwitterFetcher instead of TwitterFetcher
    """

    def __init__(self):
        self.ctm = ConvertTM()
        logging.config.dictConfig(LOGGING_DICT_CONFIG)
        self.logger = logging.getLogger('get_data')

    def fetch_user_info_from_name(self, username: str) -> User:
        """
        get incomplete user information with username
        [!!] This function is unstable. This cannot work well sometimes by query_user_info().
        :param username: screen name except first '@'
        :type username: str
        :return: User
        """
        user = User()
        try:
            user_info = twitterscraper.query_user_info(username)
            user = self.ctm.from_ts_user(user_info)

        except Exception as e:
            self.logger.error(e)

        return user

    def fetch_tweet(self, username: str = "", max_tweet: int = 0,
                    q: str = "", since: int = 0, until: int = 0) -> List[Tweet]:
        """
        collect tweets with GetOldPython3
        [!!] this method may take a lot of time, if you don't specify max tweet count.
        :param username: screen name except '@'
        :type username: str
        :param max_tweet:  max tweet count
        :type max_tweet: int
        :param q: search word
        :type q: str
        :param since: relative since date (e.g. today => 0, yesterday => 1, a week ago => 7)
        :type since: int
        :param until: relative until date (e.g. today => 0, yesterday => 1, a week ago => 7)
        :type until: int
        :return: list[Tweet]:
        """
        if since < until:
            self.logger.error("Invalid Argument: specify until date before since date")
            return []
        try:
            tc = Got.manager.TweetCriteria()
            now = datetime.now()

            if username:
                tc.setUsername(username)

            if max_tweet:
                tc.setMaxTweets(max_tweet)

            if q:
                tc.setQuerySearch(q)

            if since:
                since_date = (now - datetime.timedelta(days=since)).strftime("%Y-%m-%d")
                tc.setSince(since=since_date)

            if until:
                until_date = (now - datetime.timedelta(days=until)).strftime("%Y-%m-%d")
                tc.setUntil(until=until_date)

            tweets = list()
            g_append = tweets.append

            tmp = Got.manager.TweetManager.getTweets(tc)
            for g_tweet in tmp:
                m_t = self.ctm.from_gti_tweet(g_tweet)
                m_t.is_official = False
                g_append(m_t)

            return tweets

        except Exception as e:
            self.logger.error(e)
            return []

    @staticmethod
    def name_to_id(username: str) -> str:
        """
        convert username to user id
        :param username: screen name except first "@"
        :type username: str
        :return: str

        """
        with TwitterScraper() as ts:
            return ts.name_to_id(username)

    @staticmethod
    def id_to_name(user_id: str) -> str:
        """
        convert user id to username
        :param user_id:
        :type user_id: str
        :return: str or None
        """
        with TwitterScraper() as ts:
            return ts.id_to_name(user_id)

    @staticmethod
    def fetch_follower_list(name: str) -> List[str]:
        """
        collect specific user's follower list
        :param name: str
        :return: List[str] follower's id
        """
        follower_list = list()
        with TwitterScraper() as ts:
            follower_list = ts.follower_list(username=name)
        return follower_list

    @staticmethod
    def fetch_following_list(name: str) -> List[str]:
        """
        collect specific user's following list
        :param name: str
        :return: List[str] following user's id
        """
        following_list = list()
        with TwitterScraper() as ts:
            following_list = ts.following_list(username=name)
        return following_list
