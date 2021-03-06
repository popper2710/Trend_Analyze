import re
import urllib.request
import urllib.error
from urllib.parse import unquote
from typing import List

import trend_analyze.src.model as model
from trend_analyze.config.define import *


class ConvertTM:
    """
    This class convert to common model from twitter data with different way.
    This methods return convert object corresponding receiving object.
    (e.g. Tweepy's Tweet => Tweet, Tweepy's User => User)
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
        m_t.tweet_id = str(tpy_t.id)
        m_t.text = self._build_full_text(tpy_t)
        m_t.lang = tpy_t.lang
        m_t.retweet_count = tpy_t.retweet_count
        m_t.favorite_count = tpy_t.favorite_count
        m_t.source = tpy_t.source
        m_t.in_reply_to_status_id = str(tpy_t.in_reply_to_status_id) if tpy_t.in_reply_to_status_id else ""
        m_t.coordinates = tpy_t.coordinates if tpy_t.coordinates else ""
        m_t.place = tpy_t.place.id if tpy_t.place else ""
        m_t.created_at = tpy_t.created_at
        m_t.updated_at = datetime.now()
        m_t.hashtags = []
        m_t.urls = []
        m_t.is_official = True

        # build hashtag model
        for h in tpy_t.entities['hashtags']:
            m_hashtag = model.Hashtag()

            m_hashtag.hashtag = h['text']
            m_hashtag.start = h['indices'][0]
            m_hashtag.end = h['indices'][1]
            m_hashtag.created_at = tpy_t.created_at

            m_t.hashtags.append(m_hashtag)

        # build entity url model
        urls = self.url_p.finditer(m_t.text)
        for u in urls:
            m_url = model.EntityUrl()

            m_url.url = u.group()
            m_url.start = u.span()[0]
            m_url.end = u.span()[1]
            # NOTE: Because its process increases process time, it's commented out by default
            # m_url.expanded_url = self._expand_url(m_url.url)
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
        m_t.user.user_id = str(gti_t.author_id)
        m_t.user.screen_name = gti_t.username
        m_t.user.updated_at = datetime.now()

        created_time = gti_t.date

        # build tweet model
        m_t.tweet_id = gti_t.id
        m_t.text = gti_t.text
        m_t.retweet_count = gti_t.retweets
        m_t.favorite_count = gti_t.favorites
        m_t.created_at = created_time
        m_t.updated_at = datetime.now()
        m_t.hashtags = []
        m_t.urls = []

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
            # NOTE: Because its process increases process time, it's commented out by default
            # m_url.expanded_url = self._expand_url(m_url.url)
            m_url.created_at = created_time

            m_t.urls.append(m_url)

        return m_t

    @staticmethod
    def from_ts_user(ts_u) -> model.User:
        user = model.User()
        user.user_id = ts_u.id
        user.name = ts_u.full_name
        user.screen_name = ts_u.user
        user.location = ts_u.location
        user.followers_count = ts_u.followers
        user.following_count = ts_u.following
        user.favorites_count = ts_u.likes
        user.listed_count = ts_u.lists
        user.statuses_count = ts_u.tweets
        user.created_at = datetime.strptime(ts_u.date_joined, "%H:%M - %Y年%m月%d日")
        user.updated_at = datetime.now()
        return user

    @staticmethod
    def from_tpy_user(tpy_u) -> model.User:
        user = model.User()
        user.user_id = str(tpy_u.id)
        user.name = tpy_u.name
        user.screen_name = tpy_u.screen_name
        user.location = tpy_u.location
        user.description = tpy_u.description
        user.followers_count = tpy_u.followers_count
        user.following_count = tpy_u.friends_count
        user.listed_count = tpy_u.listed_count
        user.favorites_count = tpy_u.favourites_count
        user.statuses_count = tpy_u.statuses_count
        user.created_at = tpy_u.created_at
        user.updated_at = datetime.now()

        return user

    @staticmethod
    def build_user_relation(user: model.User, follower_list: List[model.User], following_list: List[model.User]) \
            -> List[model.UserRelation]:
        follower_set = {u.screen_name for u in follower_list}
        following_set = {u.screen_name for u in following_list}
        user_map = {u.screen_name: u for u in follower_list}
        user_map.update({u.screen_name: u for u in following_list})

        bidirectional_set = follower_set & following_set
        only_following_set = follower_set.difference(following_set)
        only_followed_set = following_set.difference(follower_set)

        def relation_builder(target: model.User, relation_id: int) -> model.UserRelation:
            user_relation = model.UserRelation()
            user_relation.user_id = user.user_id
            user_relation.username = user.screen_name
            user_relation.target_id = target.user_id
            user_relation.target_name = target.screen_name
            user_relation.relation_id = relation_id
            user_relation.updated_at = datetime.now()
            return user_relation

        user_relations = [relation_builder(user_map[target], BIDIRECTIONAL_ID) for target in bidirectional_set]
        user_relations.extend([relation_builder(user_map[target], ONLY_FOLLOWING_ID) for target in only_following_set])
        user_relations.extend([relation_builder(user_map[target], ONLY_FOLLOWED_ID) for target in only_followed_set])
        return user_relations

    @staticmethod
    def _build_full_text(tpy_t) -> str:
        if hasattr(tpy_t, "retweeted_status"):
            return "RT @" + tpy_t.retweeted_status.user.screen_name + ": " + tpy_t.retweeted_status.full_text
        else:
            return tpy_t.full_text

    @staticmethod
    def _expand_url(url) -> str:
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req) as res:
                return unquote(res.url)
        except urllib.error.HTTPError as err:
            return ""
