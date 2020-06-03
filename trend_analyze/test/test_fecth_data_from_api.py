import unittest

from trend_analyze.config.define import *
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher


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


if __name__ == '__main__':
    unittest.main()
