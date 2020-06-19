import unittest

from trend_analyze.config import *
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
        self.assertEqual(user.user_id, TEST_USER_ID)

    def test_fetch_tweet(self):
        tweet = self.tf.fetch_tweet(max_tweet=1, q="test")
        self.assertIn("test", tweet[0].text.lower())

    def test_fetch_follower_list(self):
        follower_list = self.tf.fetch_follower_list(TEST_USERNAME)
        self.assertTrue(follower_list)

    def test_fetch_following_list(self):
        following_list = self.tf.fetch_following_list(TEST_USERNAME)
        self.assertTrue(following_list)
