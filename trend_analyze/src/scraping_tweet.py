import pickle
import time
import logging
import logging.config


from trend_analyze.config import *



class TwitterScraper:
    """
    This class collects tweet data that the packages cannot collect. This is slow and unstable,
    so you should use TweetFetcher class as far as possible.
    """

    def __init__(self):
        logging.config.dictConfig(LOGGING_DICT_CONFIG)
        self.logger = logging.getLogger('scraping_tweet')

    # ========================================[public method]=========================================
    def name_to_id(self, username: str) -> (str, None):
        """
        convert username to user id
        :param username: screen name except first "@"
        :type username: str
        :return: str or None
        """
        pass

    def id_to_name(self, user_id: str) -> (str, None):
        """
        convert user id to name
        :param user_id:
        :type user_id: str
        :return: str or None
        """
        pass

    def follower_list(self, username: str) -> list:
        """
        scraping followers screen username
        :param username: screen username except first "@"
        :type username: str
        :return: [list] screen username
        """
        pass

    def following_list(self, username: str) -> list:
        """
        scraping following screen username
        :param username: scrren username except first "@"
        :type username: str
        :return: [list] screen username
        """
        pass

    # ========================================[private method]========================================

    def _collect_account_list(self, url: str) -> list:
        """
        collect user username from following or followed list page
        :param url: following or followed list url
        :type url: str
        :return: [list] accounts
        """
        pass
