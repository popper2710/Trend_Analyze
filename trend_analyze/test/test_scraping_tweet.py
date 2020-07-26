import unittest

from trend_analyze.src.scraping_tweet import TwitterScraper
from trend_analyze.config import *


class TestScrapingTweet(unittest.TestCase):
    """
    test class for scraping_tweet.py
    """

    def __init__(self, *args, **kwargs):
        super(TestScrapingTweet, self).__init__(*args, **kwargs)
        self.ts = TwitterScraper()

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_follower_list(self):
        follower_list = self.ts.follower_list(TEST_USERNAME)
        self.assertNotEqual(follower_list, [])

    def test_following_list(self):
        follower_list = self.ts.following_list(TEST_USERNAME)
        self.assertNotEqual(follower_list, [])
    def test_name_to_id(self):
        self.assertEqual(TEST_USER_ID, self.ts.name_to_id(TEST_USERNAME))
