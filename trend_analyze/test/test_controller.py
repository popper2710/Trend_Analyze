import unittest
import time

from trend_analyze.config import *
from trend_analyze.src.controller import Controller
from trend_analyze.src.db import session
from trend_analyze.src.table_model import *
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
        self.test_tweet = next(self.atf.fetch_user_tweet(TEST_USER_ID, count=1))

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'
        create_database()
        session.query(TableTweet).delete()
        session.query(TableUsersRelation).delete()
        session.commit()

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_prevent_tweet_duplicate(self):
        for _ in range(5):
            self.controller.insert_tweet(self.test_tweet)
        user_tweet = session.query(TableTweet, TableUser) \
            .filter(TableUser.t_user_id == TEST_USER_ID) \
            .filter(TableTweet.updated_at >= self.start).all()
        self.assertEqual(1, len(user_tweet))

    def test_prevent_user_duplicate(self):
        for i in range(5):
            self.controller.insert_tweet(self.test_tweet)
        user = session.query(TableUser).all()
        self.assertEqual(1, len(user))

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
