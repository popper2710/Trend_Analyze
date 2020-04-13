import unittest

from trend_analyze.src.scraping_tweet import TwitterScraper
from trend_analyze.config import *


class TestScrapingTweet(unittest.TestCase):
    """
    test class of test_scraping_tweet.py
    """
    def __init__(self, *args, **kwargs):
        super(TestScrapingTweet, self).__init__(*args, **kwargs)
        self.ts = TwitterScraper()

    def test_name_to_id(self):
        self.assertEqual(TEST_USER_ID, self.ts.name_to_id(TEST_USERNAME))
