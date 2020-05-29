import logging
import logging.config
import datetime

import GetOldTweets3 as Got
from twitterscraper.query import query_user_info

from trend_analyze.src.convert_to_model import ConvertTM
from trend_analyze.src.scraping_tweet import TwitterScraper
from trend_analyze.config import *


class TwitterFetcher:
    """
    TwitterFetcher can collect data without Api's limitation. But it may collect uncomplete information or can only
    collect parts of data. If you want to collect complete data, use ApiTwitterFetcher instead of TwitterFetcher
    """
    def __init__(self):
        self.ctm = ConvertTM()
        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('get_data')
        self.ts = TwitterScraper

    def fetch_user_info_from_name(self, username: str):
        """
        get incomplete user information with username
        :param username: screen name except first '@'
        :type username: str
        :return: query
        """
        try:
            user_info = query_user_info(username)
            user = self.ctm.from_ts_user(user_info)
        except Exception as e:
            self.logger.error(e)
            user = None

        return user

    def fetch_tweet(self, username: str = "", max_tweet: int = 0, q: str = "", since: int = 0, until: int = 0):
        """
        collect tweets with GetOldPython3
        [!!] this method may take a lot of time, if you don't specify max tweet count.
        :param username: screen name except '@'
        :type username: str
        :param max_tweet:  max tweet count
        :type max_tweet: int
        :param q: search word
        :type q: str
        :return: list[Tweet]:
        """
        if since < until:
            self.logger.error("Invalid Argument: specify until date before since date")
            return None
        try:
            tc = Got.manager.TweetCriteria()
            now = datetime.datetime.now()

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
            return None

    def fetch_follower_list(self, name: str):
        """
        collect specific user's follower list
        :param name: str
        :return: List[str]
        """
        follower_list = self.ts.follower_list(username=name)
        return follower_list

    def fetch_following_list(self, name: str):
        """
        collect specific user's following list
        :param name: str
        :return: List[str]
        """
        following_list = self.ts.following_list(username=name)
        return following_list