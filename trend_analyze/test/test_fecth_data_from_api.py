import unittest

from trend_analyze.config import *
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher
from trend_analyze.src.model.user import User


class TestFetchDataFromApi(unittest.TestCase):
    """
    test class for fetch_data_from_api.py
    """
    def __init__(self, *args, **kwargs):
        super(TestFetchDataFromApi, self).__init__(*args, **kwargs)
        self.atf = ApiTwitterFetcher(quiet=True)

    def test_fetch_followed_id_list(self):
        follower_id = self.atf.fetch_followed_id_list(TEST_USER_ID)
        self.assertNotEqual(follower_id, [])

    def test_fetch_friends_id_list(self):
        following_id = self.atf.fetch_friends_id_list(TEST_USER_ID)
        self.assertNotEqual(following_id, [])

    def test_fetch_user_info(self):
        user = self.atf.fetch_user_info(TEST_USER_ID)
        self.assertIsInstance(user, User)

    def test_fetch_user_tweet(self):
        user_tweet = self.atf.fetch_user_tweet(TEST_USER_ID)
        for i in user_tweet:
            self.assertNotEqual(i, [])
            self.assertEqual(i[0].user.user_id, TEST_USER_ID)
            break

    def test_fetch_tweet_including_target(self):
        tweet = self.atf.fetch_tweet_including_target("TEST")
        for i in tweet:
            self.assertNotEqual(i, [])
            self.assertIn("TEST", i[0].text)
            break

if __name__ == '__main__':
    unittest.main()
