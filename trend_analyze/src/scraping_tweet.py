import logging
import logging.config
import requests
from bs4 import BeautifulSoup
import datetime

from trend_analyze.src.model import User
from trend_analyze.config import *


class TwitterScraper:
    """
    This class collects tweet data that the packages cannot collect. This is slow and unstable,
    so you should use TweetFetcher class as far as possible.
    """

    def __init__(self):
        logging.config.dictConfig(LOGGING_DICT_CONFIG)
        self.logger = logging.getLogger('scraping_tweet')
        self.m_twitter_url = "https://mobile.twiiter.com"
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)'

    # ========================================[public method]=========================================

    def user_info(self, username: str) -> User:
        """
        build user object from user name
        :param username: screen name
        :return: User
        """
        url = f"{self.m_twitter_url}/{username}"
        headers = {"User-Agent": self.user_agent}
        res = requests.get(url, headers=headers)
        html = BeautifulSoup(res.text, "lxml")

        user = User()
        user.name = html.select_one("div.fullname").text
        user.screen_name = html.select_one("span.screen-name").text
        user.location = html.select_one("div.location").text
        user.description = html.select_one("td > div.bio > div").get_text().strip()
        user.statuses_count = html.select_one("td:nth-child(1) > div.statnum")
        user.following_count = html.select_one("td:nth-child(2) > a > div.statnum")
        user.follower_count = html.select_one("td.stat.stat-last > a > div.statnum")
        user.updated_at = datetime.now()

        return user

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
