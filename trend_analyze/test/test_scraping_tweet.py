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

