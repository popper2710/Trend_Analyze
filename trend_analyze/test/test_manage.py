import unittest
import datetime

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

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_update_trend_availables(self):
        self.manage.update_trend_availables()
        availables_model = TableTrendAvailable
        availables = self.session.query(availables_model.updated_at)
        time_diff = datetime.now() - availables[0]
        self.assertLessEqual(time_diff.seconds, 600)

    def test_store_user_tweet(self):
        self.manage.store_user_tweet(TEST_USER_ID)
        user_tweet = self.session.query(TableUser.updated_at)\
            .filter(TableUser.t_user_id == TEST_USER_ID)
        time_diff = datetime.now() - user_tweet[0]
        self.assertLessEqual(time_diff.seconds, 600)

    def test_store_user_tweet_n(self):
        self.manage.store_user_tweet_n(TEST_USER_ID)
        user_tweet = self.session.query(TableUser.updated_at) \
            .filter(TableUser.t_user_id == TEST_USER_ID)
        time_diff = datetime.now() - user_tweet[0]
        self.assertLessEqual(time_diff.seconds, 600)

    def test_store_tweet_including_trend(self):
        self.manage.store_tweet_including_trend(rank=1)
        top_trend_word = self.atf.fetch_current_trends(JAPAN_WOEID)[0]["trends"][0]["name"]
        trend_tweet = self.session.query(TableTweet.text) \
            .filter(TableTweet.user.t_user_id != TEST_USER_ID and
                    TableTweet.created_at >= datetime.today() - datetime.timedelta(days=1))
        self.assertIn(top_trend_word, trend_tweet[0])

    def test_store_tweet_including_word(self):
        pass

    def test_store_tweet_including_word_n(self):
        self.manage.store_tweet_including_trend(rank=2)
        second_trend_word = self.atf.fetch_current_trends(JAPAN_WOEID)[0]["trends"][1]["name"]
        trend_tweet = self.session.query(TableTweet.text) \
            .filter(TableTweet.user.t_user_id != TEST_USER_ID and
                    TableTweet.created_at >= datetime.today() - datetime.timedelta(days=1))
        self.assertIn(second_trend_word, trend_tweet[0])

    def test_store_users_relation(self):
        pass

    def test_store_users_relation_n(self):
        pass

    def test_upgrade_user(self):
        self.manage.upgrade_user(TEST_USER_ID)
        user = self.session.query(TableUser).filter(TableUser.t_user_id == TEST_USER_ID)
        time_diff = datetime.now() - user.updated_at
        self.assertLessEqual(time_diff.seconds, 600)

    def test_get_limit_status(self):
        limit = self.manage.get_limit_status()
        # It can arises Error by deviation.
        self.assertIn("rate_limit_context", limit)


if __name__ == '__main__':
    unittest.main()
