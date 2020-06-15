import unittest

from trend_analyze.config import *
from trend_analyze.src.manage import Manage


class TestManage(unittest.TestCase):
    """
    test class for manage.py
    """
    def __init__(self, *args, **kwargs):
        super(TestManage, self).__init__(*args, **kwargs)
        self.manage = Manage()

    def test_update_trend_availables(self):
        pass

    def test_store_user_tweet(self):
        pass

    def test_store_user_tweet_n(self):
        pass

    def test_store_tweet_including_trend(self):
        pass

    def test_store_tweet_including_word(self):
        pass

    def test_store_tweet_including_word_n(self):
        pass

    def test_store_users_relation(self):
        pass

    def test_store_users_relation_n(self):
        pass

    def test_upgrade_user(self):
        pass

    def test_get_limit_status(self):
        pass


if __name__ == '__main__':
    unittest.main()
