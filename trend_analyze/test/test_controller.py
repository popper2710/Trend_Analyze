import unittest
import os

from trend_analyze.config import *
from trend_analyze.src.controller import Controller


class TestController(unittest.TestCase):
    """
    test class for fetch_data_from_api.py
    """
    def __init__(self, *args, **kwargs):
        super(TestController, self).__init__(*args, **kwargs)
        self.controller = Controller

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV


if __name__ == '__main__':
    unittest.main()
