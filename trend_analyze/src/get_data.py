import tweepy
import logging
import logging.config
import datetime
import time
import GetOldTweets3 as Got

from ..config import *


class GetTweetInfo:
    def __init__(self, quiet=False):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.quiet = quiet
        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('__name__')

    # ========================================[public method]=========================================
    def get_followed_id_list(self, search_id: str):
        """
        get followed Id List for account with twitter user id passed as argument
        :param search_id: [str] twitter id
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
            return None

    def get_friends_id_list(self, search_id: str):
        """
        get following list for account with twitter user id passed as argument
        :param search_id: [str] twitter id
        :return: [list] following list
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
            return None

    def get_user_info(self, user_id: int):
        """
        receive user_id as argument and return User object
        :param user_id:
        :return: User object
        """
        user = self.api.get_user(user_id)
        user.created_at += datetime.timedelta(hours=9)
        return user

    def collect_user_tweet(self, user_id: int, count: int = 200, *args, **kwargs):
        """
        receive user_id and then return Tweet object
        :param count: [int]request count
        :param user_id:[int]
        :return tweet_list:[Generator(list)](Tweet object)

        [!!] If Target user is protected, it cannot receive tweet(response code is '401').
        """
        tweet_list = []
        t_append = tweet_list.append

        try:
            for page in tweepy.Cursor(self.api.user_timeline, user_id=user_id, count=count, *args, **kwargs).pages():
                for tweet in page:
                    tweet.is_official = True
                    t_append(tweet)
                yield tweet_list

        except tweepy.error.TweepError as err:
            self._q_logging(err.reason)

            return None

    def get_trends_available(self):
        """
        get locations that Twitter has trending topic information.
        :return: trend_list: [list]
        """
        try:
            availables = self.api.trends_available()
            return availables

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

            return None

    def collect_tweet_including_target(self, q: str, *args, **kwargs):
        """
        Returns a list of relevant Tweets including set word
        :param q:[str] search word
        :return: trend_list: [Generator(list)] tweet object
        """
        tweet_list = list()
        t_append = tweet_list.append
        try:
            for page in tweepy.Cursor(self.api.search, q, *args, **kwargs).pages():
                tweet_list = []
                for tweet in page:
                    tweet.is_official = True
                    t_append(tweet)
                    yield tweet_list

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

            return None

    def get_current_trends(self, woeid: int):
        """
        Return top 50 trending topics for a specific WOEID.
        :param exclude: remove all hashtags from the trends list.
        :type woeid: Yahoo! Wehre On Earth ID of the location to return trending
        :return
        """

        try:
            trends = self.api.trends_place(id=woeid)
            return trends

        except tweepy.error.TweepError as err:
            self._q_logging(err.message)

            return None

    def collect_tweet_by_got(self, username: str = "", max_tweet: int = 0, q: str = ""):
        """
        collect tweets with GetOldPython3
        [!!] this method may take a lot of time, if you don't specify max tweet count.
        :param q: search word
        :param username: screen name except '@'
        :param max_tweet:  max tweet count
        :return: list[got object]:
        """
        try:
            tweetCriteria = Got.manager.TweetCriteria()

            if username:
                tweetCriteria.setUsername(username)

            if max_tweet:
                tweetCriteria.setMaxTweets(max_tweet)

            if q:
                tweetCriteria.setQuerySearch(q)

            tmp = Got.manager.TweetManager.getTweets(tweetCriteria)
            g_tweets = list()
            g_append = g_tweets.append
            for g_tweet in tmp:
                g_tweet.is_official = False
                g_append(g_tweet)

            return g_tweets

        except Exception as e:
            self._q_logging(e)
            return None

    # ========================================[private method]========================================
    def _q_logging(self, msg):
        if not self.quiet:
            self.logger.error(msg)
