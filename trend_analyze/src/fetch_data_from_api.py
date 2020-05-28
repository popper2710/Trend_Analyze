import logging
import logging.config
import datetime
import time

import tweepy

from trend_analyze.src.convert_to_model import ConvertTM
from trend_analyze.config import *


class ApiTwitterFetcher:
    """
    ApiTwitterFetcher collects data with twitter api. It can collect high quality information but it are limited by the
    limitations of the API's. So if you collect data without such limitation, use TwitterFetcher instead of this.
    """

    def __init__(self, quiet=False):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.ctm = ConvertTM()
        self.quiet = quiet

        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('get_data')

    # ========================================[public method]=========================================
    def fetch_followed_id_list(self, search_id: str):
        """
        collect followed Id List for account with twitter user id passed as argument
        :type search_id: str
        :param search_id: twitter id
        :return: list: followed id List
        """
        cursor = -1
        followed_ids_list = list()
        id_append = followed_ids_list.append

        try:
            for page in tweepy.Cursor(self.api.followers_ids, id=search_id, cursor=cursor).pages():
                for followed_id in page:
                    id_append(followed_id)
            return followed_ids_list

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

            time.sleep(1)  # for rate limit
            return []

    def fetch_friends_id_list(self, search_id: str):
        """
        collect following list for account with twitter user id passed as argument
        :type search_id: str
        :param search_id: twitter id
        :return: list[int] following user id list
        """
        cursor = -1
        friends_ids = list()
        id_append = friends_ids.append

        try:
            for page in tweepy.Cursor(self.api.friends_ids, id=search_id, cursor=cursor).pages():
                for friend_id in page:
                    id_append(friend_id)
            return friends_ids

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)
            return []

    def fetch_user_info(self, user: str):
        """
        fetch user information with user_id or username as argument
        :param user: user_id or username
        :type user: str
        :return: Tweepy User object
        """
        user = self.api.get_user(user)
        user.created_at += datetime.timedelta(hours=9)
        return user

    def fetch_user_tweet(self, user_id: int, count: int = 200, *args, **kwargs):
        """
        receive user_id and then return Tweet object
        :param count: request count
        :type count: int
        :param user_id:
        :type user_id: int
        :return tweet_list:[Generator(list[Tweet])]

        [!!] If Target user is protected, it cannot receive tweet(response code is '401').
        """
        tweet_list = []
        t_append = tweet_list.append

        try:
            for page in tweepy.Cursor(self.api.user_timeline, user_id=user_id, count=count, *args, **kwargs).pages():
                for tweet in page:
                    m_t = self.ctm.from_tpy_tweet(tweet)
                    m_t.is_official = True
                    t_append(m_t)
                yield tweet_list

        except tweepy.error.TweepError as err:
            self._q_logging(err.reason)

            return None

    def fetch_tweet_including_target(self, q: str, *args, **kwargs):
        """
        Returns a list of relevant Tweets including set word
        :param q: search word
        :type q: str
        :return: trend_list: [Generator(list[Tweet])]
        """
        tweet_list = list()
        t_append = tweet_list.append
        try:
            for page in tweepy.Cursor(self.api.search, q, *args, **kwargs).pages():
                tweet_list = []
                for tweet in page:
                    m_t = self.ctm.from_tpy_tweet(tweet)
                    m_t.is_official = True
                    t_append(m_t)
                yield tweet_list

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

            return []

    def fetch_trends_available(self):
        """
        get locations that Twitter has trending topic information.
        :return: trend_list: [list]
        """
        try:
            availables = self.api.trends_available()
            return availables

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

            return []

    def fetch_current_trends(self, woeid: int):
        """
        Return top 50 trending topics for a specific WOEID.
        :param woeid: Yahoo! Where On Earth ID of the location to return trending
        :type woeid: int
        :return
        """

        try:
            trends = self.api.trends_place(id=woeid)
            return trends

        except tweepy.error.TweepError as err:
            self._q_logging(err.reason)

            return None

    def fetch_limit_status(self):
        """
        Return twitter api rate limit statuses
        :return: dict
        """
        limit_status = self.api.rate_limit_status()
        return limit_status

    # ========================================[private method]========================================
    def _q_logging(self, msg):
        if not self.quiet:
            self.logger.error(msg)
