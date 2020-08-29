import unittest

from trend_analyze.config import *
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher


class TestFetchDataFromApi(unittest.TestCase):
    """
    test class for fetch_data_from_api.py
    """

    def __init__(self, *args, **kwargs):
        super(TestFetchDataFromApi, self).__init__(*args, **kwargs)
        self.atf = ApiTwitterFetcher(quiet=True)

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_fetch_followed_id_list(self):
        follower_id = self.atf.fetch_followed_id_list(TEST_USER_ID)
        self.assertNotEqual(follower_id, [])

    def test_fetch_friends_id_list(self):
        following_id = self.atf.fetch_friends_id_list(TEST_USER_ID)
        self.assertNotEqual(following_id, [])

    def test_fetch_user_info(self):
        user = self.atf.fetch_user_info(TEST_USER_ID)
        self.assertEqual(user.user_id, TEST_USER_ID)

    def test_fetch_user_tweet(self):
        user_tweet = self.atf.fetch_user_tweet(TEST_USER_ID)
        for i in user_tweet:
            self.assertEqual(i[0].user.user_id, TEST_USER_ID)
            break

    def test_fetch_tweet_including_target(self):
        tweet = self.atf.fetch_tweet_including_target("TEST")
        for i in tweet:
            self.assertIn("test", i[0].text.lower())
            break

    def test_fetch_trend_availables(self):
        trend_availables = self.atf.fetch_trends_available()
        self.assertEqual(trend_availables[0]['name'], "Worldwide")

    def test_fetch_current_trends(self):
        trends = self.atf.fetch_current_trends(JAPAN_WOEID)
        self.assertNotEqual(trends[0]['trends'], [])


if __name__ == '__main__':
    unittest.main()
