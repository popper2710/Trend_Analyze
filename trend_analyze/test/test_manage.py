import unittest
import datetime
import os

from trend_analyze.config import *
from trend_analyze.src.manage import Manage
from trend_analyze.src.db import session
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher
from trend_analyze.src.table_model import *


class TestManage(unittest.TestCase):
    """
    test class for manage.py
    """

    def __init__(self, *args, **kwargs):
        super(TestManage, self).__init__(*args, **kwargs)
        self.manage = Manage()
        self.atf = ApiTwitterFetcher()
        self.session = session

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'
        session.query(TableTweet).delete()
        session.query(TableUsersRelation).delete()
        session.query(TableUser).delete()
        session.commit()

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_update_trend_availables(self):
        self.manage.update_trend_availables()
        availables_model = TableTrendAvailable
        availables = self.session.query(availables_model.updated_at).all()
        time_diff = datetime.now() - availables[0].updated_at
        self.assertLessEqual(time_diff.seconds, 600)

    def test_store_user_tweet(self):
        start = datetime.now()
        self.manage.store_user_tweet(TEST_USER_ID)
        user_tweet = self.session.query(TableTweet) \
            .filter(TableTweet.user.t_user_id == TEST_USER_ID and TableTweet.updated_at > start).all()
        self.assertEqual(TEST_USER_ID, user_tweet.user.t_user_id)

    def test_store_user_tweet_n(self):
        start = datetime.now()
        self.manage.store_user_tweet_n(TEST_USER_ID)
        user_tweet = self.session.query(TableTweet) \
            .filter(TableTweet.user.t_user_id == TEST_USER_ID and TableTweet.updated_at > start).all()
        self.assertEqual(TEST_USER_ID, user_tweet.user.t_user_id)

    def test_store_tweet_including_trend(self):
        start = datetime.now()
        self.manage.store_tweet_including_trend(rank=1)
        top_trend_word = self.atf.fetch_current_trends(JAPAN_WOEID)[0]["trends"][0]["name"]
        trend_tweet = self.session.query(TableTweet.text) \
            .filter(TableTweet.user.t_user_id != TEST_USER_ID and
                    TableTweet.updated_at > start).all()
        self.assertIn(top_trend_word, trend_tweet[0].text.lower())

    def test_store_tweet_including_word(self):
        start = datetime.now()
        testword = "Analyze"
        self.manage.store_tweet_including_word(testword)
        including_tweet = self.session.query(TableTweet).filter(TableTweet.updated_at > start).all()
        self.assertIn(testword, including_tweet[0].lower())

    def test_store_tweet_including_word_n(self):
        start = datetime.now()
        testword = "Essays"
        self.manage.store_tweet_including_word_n(testword)
        including_tweet = self.session.query(TableTweet.text).filter(TableTweet.updated_at > start).all()
        self.assertIn(testword, including_tweet[0].lower())

    def test_store_users_relation(self):
        start = datetime.now()
        self.manage.store_users_relation(TEST_USER_ID)
        user_relations = self.session.query(TableUsersRelation) \
            .filter(TableUsersRelation.user_id == TEST_USER_ID and TableUsersRelation.updated_at >= start).all()
        self.assertGreaterEqual(1, len(user_relations))

    def test_store_users_relation_n(self):
        start = datetime.now()
        self.manage.store_users_relation_n(TEST_USER_ID)
        user_relations = self.session.query(TableUsersRelation) \
            .filter(TableUsersRelation.user_id == TEST_USER_ID and TableUsersRelation.updated_at >= start).all()
        self.assertGreaterEqual(1, len(user_relations))

    def test_upgrade_user(self):
        start = datetime.now()
        self.manage.upgrade_user(TEST_USER_ID)
        user = self.session.query(TableUser) \
            .filter(TableUser.t_user_id == TEST_USER_ID and TableUser.updated_at >= start).all()
        self.assertGreaterEqual(1, len(user))

    def test_get_limit_status(self):
        limit = self.manage.get_limit_status()
        # It can arises Error by deviation.
        self.assertIn("rate_limit_context", limit)


if __name__ == '__main__':
    unittest.main()
