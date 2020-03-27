import os
import sys
import tweepy
import logging
import logging.config
import datetime
import time

sys.path.append('../')
from config import *


class GetTweetInfo:
    def __init__(self, quiet=False):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.quiet = quiet
        conf_path = PROJECT_ROOT+"config\logging.ini"
        print(conf_path)
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('__name__')

    # ========================================[public method]=========================================
    def get_followed_id_list(self, search_id, limit=0):
        """
        get followed Id List for account with twitter user id passed as argument
        :param search_id: twitter id (str)
        :param limit: limit to get id (int)
        :return: list: followed id List
        """
        cursor = -1
        while cursor != 0:
            global followed_ids_list
            followed_ids = tweepy.Cursor(self.api.followers_ids, id=search_id, cursor=cursor).pages(limit)

            try:
                followed_ids_list = [i for i in followed_ids]

            except tweepy.error.TweepError as e:
                self._q_logging(e.reason)

            time.sleep(60)  # for rate limit

            return followed_ids_list[0]

    def get_friends_id_list(self, search_id, limit=0):
        """
        get following list for account with twitter user id passed as argument
        :param search_id: twitter id (str)
        :param limit: limit to get id (int)
        :return: list following list
        """
        global following_ids_list
        friends_ids = tweepy.Cursor(self.api.friends_ids, id=search_id, cursor=-1).items(limit)

        try:
            following_ids_list = [i for i in friends_ids]

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

        return following_ids_list

    def get_user_info(self, user_id):
        """
        receive user_id as argument and return User object
        :param user_id:
        :return: User object
        """
        user = self.api.get_user(user_id)
        user.created_at += datetime.timedelta(hours=9)
        return user

    def get_tweet(self, user_id, *args, **kwargs):
        """
        receive user_id and then return Tweet object
        :param user_id:int
        :return tweet_list:list(Tweet object)

        [!!] If Target user is protected, it cannot receive tweet(response code is '401').
        """
        tweet_list = []

        try:
            for page in tweepy.Cursor(self.api.user_timeline, user_id=user_id, count=200, *args, **kwargs).pages():
                for tweet in page:
                    tweet.created_at += datetime.timedelta(hours=9)  # change to JST from GMT
                    tweet_list.append(tweet)

            return tweet_list

        except tweepy.error.TweepError as err:
            self._q_logging(err.reason)

            return None


    def get_trends_available(self):
        """
        get locations that Twitter has trending topic information.
        :return: trend_list: list
        """
        try:
            availables = self.api.trends_available()
            return availables

        except tweepy.error.TweepError as e:
            self._q_logging(e.reason)

            return None

    def get_tweet_related_trend(self, q, *args, **kwargs):
        """
        Returns a list of relevant Tweets including trend word
        :return: trend_list: list
        """
        trends = self._get_current_trend(woeid=woeid)
        tweet_list = []
        t_append = tweet_list.append
        try:
            for page in tweepy.Cursor(self.api.search, q, *args, **kwargs).pages():
                for tweet in page:
                    tweet.created_at += datetime.timedelta(hours=9)  # change to JST from GMT
                    t_append(tweet)

            return tweet_list

        except tweepy.error.TweepError as e:

            return None

    # ========================================[private method]========================================
    def _get_current_trend(self, woeid, exclude=[]):
        """
        Return top 50 trending topics for a specific WOEID.
        :param exclude: remove all hashtags from the trends list.
        :type woeid: Yahoo! Wehre On Earth ID of the location to return trending
        :return
        """

        try:
            trends = self.api.trends_place(woeid=woeid, exclude=exclude)
            return trends

        except tweepy.error.TweepError as err:
            self._q_logging(err.reason)

            return None

    def _q_logging(self, msg):
        if not self.quiet:
            self.logger.error(msg)


if __name__ == '__main__':
    gti = GetTweetInfo()
    availables = gti.get_tweet(123)
    print(availables[0])
