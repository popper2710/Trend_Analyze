import re
from datetime import datetime

import trend_analyze.src.model as model


class ConvertTM:
    """
    This class convert to common model from twitter data with different way.
    This methods return convert object corresponding receiving object.
    (e.g. Tweepy Tweet => Tweet, twitterscraper User => User)
    """
    def __init__(self):
        self.url_p = re.compile(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+')
        self.hashtag_p = re.compile(r'[#＃][Ａ-Ｚａ-ｚA-Za-z一-鿆0-9０-９ぁ-ヶｦ-ﾟー._-]+')

    def from_tpy_tweet(self, tpy_t) -> model.Tweet:
        """
        From: Tweepy Tweet Object
        :param tpy_t:
        :return: Tweet
        """
        m_t = model.Tweet()

        # build user model
        m_t.user = self.from_tpy_user(tpy_t.user)

        # build tweet model
        m_t.tweet_id = tpy_t.id
        m_t.text = tpy_t.text
        m_t.lang = tpy_t.lang
        m_t.retweet_count = tpy_t.retweet_count
        m_t.favorite_count = tpy_t.favorite_count
        m_t.source = tpy_t.source
        m_t.in_reply_to_status_id = tpy_t.in_reply_to_status_id
        m_t.coordinates = tpy_t.coordinates
        m_t.place = tpy_t.place
        m_t.created_at = tpy_t.created_at

        # build hashtag model
        for h in tpy_t.entities['hashtags']:
            m_hashtag = model.Hashtag()

            m_hashtag.hashtag = h['text']
            m_hashtag.start = h['indices'][0]
            m_hashtag.end = h['indices'][1]
            m_hashtag.created_at = tpy_t.created_at

            m_t.hashtags.append(m_hashtag)

        # build entity url model
        for u in tpy_t.entities['urls']:
            m_url = model.EntityUrl()
            m_url.url = u['url']
            m_url.start = u['indices'][0]
            m_url.end = u['indices'][1]
            m_url.created_at = tpy_t.created_at

            m_t.urls.append(m_url)

        return m_t

    def from_gti_tweet(self, gti_t) -> model.Tweet:
        """
        From : Get Old Tweet 3 Tweet Object
        :param gti_t: got object
        :return: Tweet
        """
        m_t = model.Tweet()

        # build user model
        m_t.user.user_id = gti_t.author_id
        m_t.user.screen_name = gti_t.username
        m_t.user.updated_at = datetime.now()

        created_time = gti_t.date

        # build tweet model
        m_t.tweet_id = gti_t.id
        m_t.text = gti_t.text
        m_t.retweet_count = gti_t.retweets
        m_t.favorite_count = gti_t.favorites
        m_t.created_at = created_time

        # build hashtag model
        hashtags = self.hashtag_p.finditer(gti_t.text)
        for h in hashtags:
            m_hashtag = model.Hashtag()

            m_hashtag.hashtag = h.group()[1:]
            m_hashtag.start = h.span()[0]
            m_hashtag.end = h.span()[1]
            m_hashtag.created_at = created_time

            m_t.hashtags.append(m_hashtag)

        # build entity url model
        urls = self.url_p.finditer(gti_t.text)
        for u in urls:
            m_url = model.EntityUrl()

            m_url.url = u.group()
            m_url.start = u.span()[0]
            m_url.end = u.span()[1]
            m_url.created_at = created_time

            m_t.urls.append(m_url)

        return m_t

    @staticmethod
    def from_tpy_user(tpy_u) -> model.User:
        user = model.User()
        user.user_id = tpy_u.id
        user.name = tpy_u.name
        user.screen_name = tpy_u.screen_name
        user.location = tpy_u.location
        user.description = tpy_u.description
        user.followers_count = tpy_u.followers_count
        user.listed_count = tpy_u.listed_count
        user.favorites_count = tpy_u.favorites_count
        user.statuses_count = tpy_u.statuses_count
        user.created_at = tpy_u.created_at
        user.updated_at = datetime.now()

        return user