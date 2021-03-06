import unittest

from trend_analyze.config import *
from trend_analyze.src.model import *
from trend_analyze.src.fetch_data import TwitterFetcher


class TestFetchData(unittest.TestCase):
    """
    test class for fetch_data.py
    """

    def __init__(self, *args, **kwargs):
        super(TestFetchData, self).__init__(*args, **kwargs)
        self.tf = TwitterFetcher()

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def __del__(self):
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_fetch_user_info_from_name(self):
        user = self.tf.fetch_user_info_from_name(TEST_USERNAME)
        self.assertEqual(TEST_USERNAME, user.screen_name)

    def test_fetch_tweet(self):
        tweet = self.tf.fetch_tweet(max_tweet=1, q="test")
        self.assertIn("test", tweet[0].text.lower())

    def test_fetch_user_relations(self):
        user_relations = self.tf.fetch_user_relations(TEST_USERNAME)
        self.assertIsInstance(user_relations[0], UserRelation)

