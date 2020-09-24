import logging
import logging.config
from datetime import timedelta
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

        logging.config.dictConfig(LOGGING_DICT_CONFIG)
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
        user.created_at += timedelta(hours=9)
        user = ConvertTM.from_tpy_user(user)
        return user

    def fetch_user_tweet(self, user_id: str, max_tweet: int = -1, unit_size: int = 200, *args, **kwargs):
        """
        receive user_id and then return Tweet object
        :param max_tweet: maximum number of tweets to fetch (By default, this is unlimited)
        :type max_tweet: int
        :param user_id:
        :type user_id: str
        :param unit_size: list size yielded once
        :type unit_size: int
        :return tweet_list:[Generator(list[Tweet])]

        [!!] If Target user is protected, it cannot receive tweet(response code is '401').
        """

        try:
            tweet_list = []
            tweet_total_num = 0
            for page in tweepy.Cursor(self.api.user_timeline, user_id=user_id,
                                      tweet_mode="extended", *args, **kwargs).pages():
                t_append = tweet_list.append
                for tweet in page:
                    if 0 <= max_tweet == tweet_total_num:
                        yield tweet_list
                        return
                    tweet_total_num += 1
                    m_t = self.ctm.from_tpy_tweet(tweet)
                    t_append(m_t)
                    if len(tweet_list) == unit_size:
                        yield tweet_list
                        tweet_list.clear()
            if tweet_list:
                yield tweet_list

        except tweepy.error.TweepError as err:
            self._q_logging(err.reason)

            return None

    def fetch_tweet_including_target(self, q: str, is_RT: bool, is_name: bool, max_tweet: int = -1,
                                     unit_size: int = 200, *args,
                                     **kwargs):
        """
        Returns a list of relevant Tweets including set word
        :param q: search word
        :type q: str
        :param max_tweet: maximum number of tweets to fetch (By default, this is unlimited)
        :type max_tweet: int
        :param is_name: if  it's true, you can fetch the tweet posted by the user having username including target word
        :param unit_size: list size yielded once
        :type unit_size: int
        :param is_RT: if it's true, you can fetch RT including target word
        :return: trend_list: [Generator(list[Tweet])]
        """
        try:
            tweet_list = list()
            tweet_total_num = 0
            keyword = q
            if is_RT:
                keyword += "filter:retweets"
            if is_name:
                keyword += "OR @i"

            for page in tweepy.Cursor(self.api.search, keyword, tweet_mode='extended', *args, **kwargs).pages():
                t_append = tweet_list.append
                for tweet in page:
                    if 0 <= max_tweet == tweet_total_num:
                        yield tweet_list
                        return
                    tweet_total_num += 1
                    m_t = self.ctm.from_tpy_tweet(tweet)
                    t_append(m_t)
                    if len(tweet_list) == unit_size:
                        yield tweet_list
                        tweet_list.clear()
            if tweet_list:
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
