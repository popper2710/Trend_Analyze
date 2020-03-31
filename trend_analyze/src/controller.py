import time
import re

from db import session
import model


class Controller:
    def __init__(self):
        self.session = session

    def insert_trend_availables(self, availables):
        """
        update table with current trend available location
        :return: None
        """
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
        availables = model.TrendAvailable
        woeids = self.session.query(availables.woeid)\
                     .filter(availables.countrycode == countrycode)\
                     .all()
        return woeids

    def insert_tweet(self, tweets: list) -> None:
        """
        insert tweet data from tweepy object
        :param tweets: tweepy object list
        :return None
        """
        items = list()
        append = items.append
        users_id = set(self.session.query(model.User.t_user_id).all())

        # =========[user data insert process]==========
        for tweet in tweets:
            item = dict()

            # except duplicate
            if tweet.user.id in users_id:
                continue
            else:
                users_id.add(tweet.user.id)

            item['user_id'] = tweet.user.id
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
            t_item['favorite_count'] = tweet.favorites_count
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

    def insert_tweet_from_got(self, tweets: list) -> None:
        """
        insert tweet getting with GetOldTweet data from tweepy object
        :param tweets: tweepy object list
        :return None
        """
        items = list()
        append = items.append
        users = self.session.query(model.User.t_user_id).all()
        users_id = {int(user.t_user_id) for user in users}

        # =========[user data insert process]==========
        for tweet in tweets:
            item = dict()

            # except duplicate
            if tweet.author_id in users_id:
                continue
            else:
                users_id.add(tweet.author_id)

            item['user_id'] = tweet.author_id
            item['screen_name'] = tweet.username
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        if items:
            self.session.execute(model.User.__table__.insert(), items)
            self.session.commit()
        # ==================[end]======================

        users_id = self.session.query(model.User.id, model.User.t_user_id).all()
        users_id = {int(user.t_user_id): user.id for user in users_id}

        t_items, eu_items, eh_items = list(), list(), list()
        t_append, eu_append, eh_append = t_items.append, eu_items.append, eh_items.append
        # for extracting hashtag and urls
        url_p = re.compile(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+')
        hashtag_p = re.compile(r'[#＃][Ａ-Ｚａ-ｚA-Za-z一-鿆0-9０-９ぁ-ヶｦ-ﾟー._-]+')
        stored_tweet_id = set(self.session.query(model.Tweet.t_tweet_id).all())

        for tweet in tweets:
            # =======[build Tweet row data]===========
            if tweet.id in stored_tweet_id:
                continue
            else:
                stored_tweet_id.add(tweet.id)

            created_time = tweet.date.strftime('%Y-%m-%d %H:%M:%S')
            t_item = dict()
            t_item['tweet_id'] = tweet.id
            t_item['user_id'] = users_id[tweet.author_id]
            t_item['text'] = tweet.text
            t_item['retweet_count'] = tweet.retweets
            t_item['favorite_count'] = tweet.favorites
            t_item['created_at'] = created_time
            t_append(t_item)
            # ==================[end]=================

            # ========[build Entity row data]=========
            hashtags = hashtag_p.finditer(tweet.text)
            for h in hashtags:
                eh_item = dict()
                eh_item['tweet_id'] = tweet.id
                eh_item['hashtag'] = h.group()
                eh_item['start'] = h.span()[0]
                eh_item['end'] = h.span()[1]
                eh_item['created_at'] = created_time
                eh_append(eh_item)

            urls = url_p.finditer(tweet.text)
            for u in urls:
                eu_item = dict()
                eu_item['tweet_id'] = tweet.id
                eu_item['url'] = u.group()
                eu_item['start'] = u.span()[0]
                eu_item['end'] = u.span()[1]
                eu_item['created_at'] = created_time
                eu_append(eu_item)

            # ==================[end]=================

        if t_items:
            self.session.execute(model.Tweet.__table__.insert(), t_items)
            self.session.commit()
        if eu_items:
            self.session.execute(model.HashTag.__table__.insert(), eh_items)
        if eh_items:
            self.session.execute(model.EntityUrl.__table__.insert(), eu_items)
        self.session.commit()

def main():
    pass


if __name__ == '__main__':
    c = Controller()
