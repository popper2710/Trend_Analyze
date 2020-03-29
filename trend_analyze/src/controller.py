import time
import re

from get_data import GetTweetInfo
from db import session
import model


class Controller:
    def __init__(self):
        self.session = session
        self.gti = GetTweetInfo()

    def update_trend_available(self):
        """
        update table with current trend available location
        :return: None
        """
        availables = self.gti.get_trends_available()
        items = list()
        append = items.append

        # initialize trend available table
        self.session.execute("DELETE FROM {}".format(model.TrendAvailable.__tablename__))

        for available in availables:
            item = dict()
            item['name'] = available['name']
            item['url'] = available['url']
            item['country'] = available['country']
            item['woeid'] = available['woeid']
            item['countrycode'] = available['countryCode']
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        self.session.execute(model.TrendAvailable.__table__.insert(), items)
        self.session.commit()

    def get_woeid(self, countrycode="JP"):
        """
        Returns woeid list correspond countrycode
        :param countrycode: str
        :return:woeids list
        """
        trendavailable = model.TrendAvailable
        woeids = self.session.query(trendavailable.woeid)\
                     .filter(trendavailable.countrycode == countrycode)\
                     .all()
        return woeids

    def _insert_tweet(self, tweets: list) -> None:
        """
        insert tweet data from tweepy object
        :param tweets: tweepy object list
        :return None
        """
        items = list()
        append = items.append
        users = self.session.query(model.User.t_user_id).all()
        users_id = {user.id for user in users}
        seen_user = list()
        s_append = seen_user.append

        # =========[user data insert process]==========
        for tweet in tweets:
            item = dict()

            # except duplicate
            if tweet.user.id in users_id:
                continue

            if tweet.user.id in seen_user:
                continue
            else:
                s_append(tweet.user.id)

            item['t_user_id'] = tweet.user.id
            item['name'] = tweet.user.name
            item['screen_name'] = tweet.user.screen_name
            item['location'] = tweet.user.location
            item['description'] = tweet.user.description
            item['followers_count'] = tweet.user.followers_count
            item['friends_count'] = tweet.user.friends_count
            item['listed_count'] = tweet.user.listed_count
            item['favorites_count'] = tweet.user.favorites_count
            item['statuses_count'] = tweet.user.statuses_count
            item['created_at'] = tweet.user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        self.session.execute(model.User.__table__.insert(), items)
        self.session.commit()
        # ==================[end]======================

        users_id = self.session.query(model.User.id, model.User.t_user_id).all()
        users_id = {user.t_user_id: user.id for user in users_id}

        t_items, eu_items, eh_items = list(), list(), list()
        t_append, eu_append, eh_append = t_items.append, eu_items.append, eh_items.append
        # for source
        p = re.compile(r'>(.*)<')

        for tweet in tweets:
            # =======[build Tweet row data]===========
            t_item = dict()
            t_item['name'] = tweet.name
            t_item['tweet_id'] = tweet.id
            t_item['user_id'] = users_id[tweet.user.id]
            t_item['text'] = tweet.text
            t_item['lang'] = tweet.lang
            t_item['retweet_count'] = tweet.retweet_count
            t_item['favorites_count'] = tweet.favorites_count
            t_item['source'] = p.findall(tweet.source)[0]
            t_item['in_reply_to_status_id'] = tweet.in_reply_to_status_id
            t_item['coordinates'] = tweet.coordinates
            t_item['place'] = tweet.place
            t_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
            t_append(t_item)
            # ==================[end]=================

            # ========[build Entity row data]=========
            for h in tweet.entities.hashtags:
                eh_item = dict()
                eh_item['tweet_id'] = tweet.id
                eh_item['hashtag'] = h.text
                eh_item['start'] = h.indices[0]
                eh_item['end'] = h.indices[1]
                eh_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                eh_append(eh_item)

            for u in tweet.entities.urls:
                eu_item = dict()
                eu_item['tweet_id'] = tweet.id
                eu_item['url'] = u.url
                eh_item['start'] = u.indices[0]
                eh_item['end'] = u.indices[1]
                eu_item['created_at'] = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
                eu_append(eu_item)

            # ==================[end]=================

        self.session.execute(model.Tweet.__table__.insert(), items)
        self.session.commit()
        self.session.execute(model.HashTag.__table__.insert(), eh_items)
        self.session.execute(model.EntityUrl.__table__.insert(), eu_items)
        self.session.commit()


def main():
    pass


if __name__ == '__main__':
    c = Controller()
    c.update_trend_available()
