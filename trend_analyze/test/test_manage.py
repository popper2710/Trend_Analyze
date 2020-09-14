import unittest
import datetime
import time

from trend_analyze.config import *
from trend_analyze.src.manage import Manage
from trend_analyze.src.db import session
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher
from trend_analyze.src.table_model import *

TEST_WORD = "Analyze"


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
        create_database()
        session.query(TableUser).delete()
        session.query(TableTweet).delete()
        session.query(TableUsersRelation).delete()
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
        time.sleep(1)
        self.manage.store_user_tweet(TEST_USER_ID, max_tweet=20)
        user_tweets = session.query(TableTweet, TableUser) \
            .filter(TableUser.t_user_id == TEST_USER_ID) \
            .filter(TableTweet.updated_at >= start).all()
        if not user_tweets:
            self.fail("Cannot acquire target tweets")
        for user_tweet in user_tweets:
            self.assertEqual(TEST_USER_ID, user_tweet.TableUser.t_user_id)

    def test_store_user_tweet_n(self):
        start = datetime.now()
        time.sleep(1)
        self.manage.store_user_tweet_n(TEST_USERNAME)
        user_tweets = session.query(TableTweet, TableUser) \
            .filter(TableUser.t_user_id == TEST_USER_ID) \
            .filter(TableTweet.updated_at >= start).all()
        if not user_tweets:
            self.fail("Cannot acquire target tweets")
        for user_tweet in user_tweets:
            self.assertEqual(TEST_USER_ID, user_tweet.TableUser.t_user_id)

    def test_store_tweet_including_trend(self):
        start = datetime.now()
        time.sleep(1)
        self.manage.store_tweet_including_trend(rank=1, max_tweet=20)
        top_trend_word = self.atf.fetch_current_trends(JAPAN_WOEID)[0]["trends"][0]["name"]
        trend_tweets = self.session.query(TableTweet, TableUser) \
            .filter(TableTweet.user_id == TableUser.id) \
            .filter(TableUser.t_user_id != TEST_USER_ID) \
            .filter(TableTweet.updated_at >= start).all()
        if not trend_tweets:
            self.fail("Cannot acquire target tweets")
        for trend_tweet in trend_tweets:
            self.assertIn(top_trend_word.lower(), trend_tweet.TableTweet.text.lower())

    def test_store_tweet_including_word(self):
        start = datetime.now()
        time.sleep(1)
        self.manage.store_tweet_including_word(TEST_WORD, max_tweet=20)
        including_tweets = self.session.query(TableTweet).filter(TableTweet.updated_at >= start).all()
        if not including_tweets:
            self.fail("Cannot acquire target tweets")
        for including_tweet in including_tweets:
            self.assertIn(TEST_WORD.lower(), including_tweet.text.lower())

    def test_store_tweet_including_word_n(self):
        start = datetime.now()
        time.sleep(1)
        self.manage.store_tweet_including_word_n(TEST_WORD, max_tweet=20)
        including_tweets = self.session.query(TableTweet).filter(TableTweet.updated_at >= start).all()
        if not including_tweets:
            self.fail("Cannot acquire target tweets")
        for including_tweet in including_tweets:
            if not TEST_WORD.lower() in including_tweet.text.lower():
                print(TEST_WORD)
            self.assertIn(TEST_WORD.lower(), including_tweet.text.lower())

    def test_store_users_relation(self):
        start = datetime.now()
        time.sleep(1)
        self.manage.store_users_relation(TEST_USER_ID)
        user_relations = self.session.query(TableUsersRelation) \
            .filter(TableUsersRelation.user_id == TEST_USER_ID and TableUsersRelation.updated_at >= start).all()
        self.assertGreaterEqual(1, len(user_relations))

    def test_store_users_relation_n(self):
        start = datetime.now()
        time.sleep(1)
        self.manage.store_users_relation_n(TEST_USER_ID)
        user_relations = self.session.query(TableUsersRelation) \
            .filter(TableUsersRelation.user_id == TEST_USER_ID and TableUsersRelation.updated_at >= start).all()
        self.assertGreaterEqual(1, len(user_relations))

    def test_upgrade_user(self):
        start = datetime.now()
        time.sleep(1)
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
