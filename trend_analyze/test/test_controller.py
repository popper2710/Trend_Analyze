import unittest
import time

from trend_analyze.config import *
from trend_analyze.src.controller import Controller
from trend_analyze.src.db import session
from trend_analyze.src.table_model import *
from trend_analyze.test.create_sample import Sample
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher


class TestController(unittest.TestCase):
    """
    test class for controller.py
    """

    def __init__(self, *args, **kwargs):
        super(TestController, self).__init__(*args, **kwargs)
        self.controller = Controller()
        self.atf = ApiTwitterFetcher()
        self.start = datetime.now()
        time.sleep(1)
        self.sample = Sample()
        self.sample.update_all()

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'
        create_database()
        self.delete_records()

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_insert_tweet(self):
        self.delete_records()
        try:
            self.controller.insert_tweet(tweets=self.sample.tweets_sample())
        except Exception as e:
            self.fail(e)

    def test_insert_user(self):
        self.delete_records()
        try:
            self.controller.insert_user(users=self.sample.users_sample())
        except Exception as e:
            self.fail(e)

    def test_prevent_tweet_duplicate(self):
        self.delete_records()
        sample_tweets = self.sample.tweets_sample()
        for _ in range(5):
            self.controller.insert_tweet(sample_tweets)
        user_tweet = session.query(TableTweet, TableUser) \
            .filter(TableUser.t_user_id == TEST_USER_ID) \
            .filter(TableTweet.updated_at >= self.start).all()
        self.assertEqual(len(sample_tweets), len(user_tweet))

    def test_prevent_user_duplicate(self):
        self.delete_records()
        sample_tweets = self.sample.tweets_sample()
        for i in range(5):
            self.controller.insert_tweet(sample_tweets)
        user = session.query(TableUser).all()
        self.assertEqual(len({tweet.user.user_id for tweet in sample_tweets}), len(user))

    def test_execute_sql(self) -> None:
        """
        This test checks whether following sql statement that can be executed with no error.
        Therefore, this test doesn't indicate that "execute_sql" can execute any sql statement.
        TEST STATEMENT: 'SELECT VERSION()'
        """
        try:
            test_sql = "SELECT VERSION()"
            _ = self.controller.execute_sql(sql=test_sql)
        except Exception as e:
            self.fail(e)

    @staticmethod
    def delete_records():
        session.query(TableTweet).delete()
        session.query(TableUser).delete()
        session.query(TableUsersRelation).delete()
        session.commit()
