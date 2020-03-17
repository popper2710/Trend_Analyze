import sys
sys.path.append('../')
import tweepy
from config import *
import datetime
import time


class GetTweetInfo:
    def __init__(self, quiet=False):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.quiet = quiet

    def get_followed_id_list(self, search_id, limit=0):
        """
        get followed Id List for account with twitter user id passed as argument
        argument:search_id -> twitter id (str)
                 limit     -> limit to get id (int)
        return : followed id List (list)
        """
        cursor = -1
        while cursor != 0:
            global followed_ids_list
            followed_ids = tweepy.Cursor(self.api.followers_ids, id=search_id, cursor=cursor).pages(limit)

            try:
                followed_ids_list = [i for i in followed_ids]

            except tweepy.error.TweepError as e:
                self.q_print(e.reason)

            time.sleep(60)  # for rate limit

            return followed_ids_list[0]

    def get_friends_id_list(self, search_id, limit=0):
        """
        get following list for account with twitter user id passed as argument
        argument:search_id -> twitter id (str)
                 limit -> limit to get id (int)
        return : following list (list)
        """
        global following_ids_list
        friends_ids = tweepy.Cursor(self.api.friends_ids, id=search_id, cursor=-1).items(limit)

        try:
            following_ids_list = [i for i in friends_ids]

        except tweepy.error.TweepError as e:
            self.q_print(e.reason, file=sys.stderr)

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

        except tweepy.error.TweepError as err:
            self.q_print(err.reason, file=sys.stderr)

            return None

        return tweet_list

    def q_print(self, *args, **kwargs):
        if not self.quiet:
            print(*args, **kwargs)


if __name__ == '__main__':
    gti = GetTweetInfo()
    tweets = gti.get_tweet(1099996270947528704)
    print(tweets[0])
