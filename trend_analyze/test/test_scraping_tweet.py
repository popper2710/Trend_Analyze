import unittest

from trend_analyze.src.scraping_tweet import TwitterScraper
from trend_analyze.config import *


class TestScrapingTweet(unittest.TestCase):
    """
    test class for scraping_tweet.py
    """

    def __init__(self, *args, **kwargs):
        super(TestScrapingTweet, self).__init__(*args, **kwargs)

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_name_to_id(self):
        with TwitterScraper() as ts:
            self.assertEqual(ts.name_to_id(TEST_USERNAME), TEST_USER_ID)

    def test_id_to_name(self):
        with TwitterScraper() as ts:
            self.assertEqual(ts.id_to_name(TEST_USER_ID), TEST_USERNAME)

    def test_follower_list(self):
        with TwitterScraper() as ts:
            follower_list = ts.follower_list(TEST_USERNAME)
            self.assertIsInstance(follower_list, list)
            self.assertNotEqual(follower_list, [])

    def test_following_list(self):
        with TwitterScraper() as ts:
            following_list = ts.following_list(TEST_USERNAME)
            self.assertIsInstance(following_list, list)
            self.assertNotEqual(following_list, [])

    def test_login_error(self):
        """
        It checks if raise error when login is failed.
        """
        ts = TwitterScraper()
        ts.twi_pass = "InvalidPassword"
        self.assertTrue(not ts._login(cookie_cache=False))
