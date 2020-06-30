import unittest
import os

from trend_analyze.config import *
from trend_analyze.src.controller import Controller
from trend_analyze.src.db import session
from trend_analyze.src.table_model import *


class TestController(unittest.TestCase):
    """
    test class for controller.py
    """
    def __init__(self, *args, **kwargs):
        super(TestController, self).__init__(*args, **kwargs)
        self.controller = Controller

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'
        session.query(TableTweet).delete()
        session.query(TableUsersRelation).delete()
        session.query(TableUser).delete()
        session.commit()

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_execute_sql(self) -> None:
        """
        This test checks whether the sql statement that can be executed in any situation is executed.
        TEST STATEMENT: 'SELECT VERSION()'
        """
        try:
            test_sql = "SELECT VERSION()"
            result = self.controller.execute_sql(sql=test_sql)
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
