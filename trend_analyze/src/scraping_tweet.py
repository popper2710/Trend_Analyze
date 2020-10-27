import logging
import logging.config
import requests
from bs4 import BeautifulSoup
import datetime
from typing import List
import random

from trend_analyze.src.model import User
from trend_analyze.config import *

user_agent_list = ['Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                   'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)']


class TwitterScraper:
    """
    This class collects tweet data that the packages cannot collect. This is slow and unstable,
    so you should use TweetFetcher class as far as possible.
    """

    def __init__(self):
        logging.config.dictConfig(LOGGING_DICT_CONFIG)
        self.logger = logging.getLogger('scraping_tweet')
        self.m_twitter_url = "https://mobile.twitter.com"
        self.twitter_url = "https://twitter.com"

    # ========================================[public method]=========================================

    def user_info(self, username: str) -> User:
        """
        build user object from user name
        :param username: screen name
        :return: User
        """
        url = f"{self.m_twitter_url}/{username}"
        headers = {"User-Agent": random.choice(user_agent_list)}
        res = requests.get(url, headers=headers)
        html = BeautifulSoup(res.text, "lxml")

        user = User()
        user.name = html.select_one("div.fullname").text
        user.screen_name = html.select_one("span.screen-name").text
        user.location = html.select_one("div.location").text
        user.description = html.select_one("td > div.bio > div").get_text().strip()
        user.statuses_count = int(html.select_one("td:nth-child(1) > div.statnum").text)
        user.following_count = int(html.select_one("td:nth-child(2) > a > div.statnum").text)
        user.follower_count = int(html.select_one("td.stat.stat-last > a > div.statnum").text)
        user.updated_at = datetime.now()

        return user

    def follower_list(self, username: str) -> List[User]:
        """
        scraping followers screen username
        :param username: screen username except first "@"
        :type username: str
        :return: [list] User
        """
        url = f"{self.twitter_url}/{username}/followers"
        return self._collect_account_list(url)

    def following_list(self, username: str) -> List[User]:
        """
        scraping following screen username
        :param username: screen username except first "@"
        :type username: str
        :return: [list] User
        """
        url = f"{self.twitter_url}/{username}/following"
        return self._collect_account_list(url)

    # ========================================[private method]========================================

    def _collect_account_list(self, url: str) -> List[User]:
        """
        collect user username from following or followed list page
        :param url: following or followed list url
        :type url: str
        :return: List[str(username)]
        """
        headers = {"User-Agent": random.choice(user_agent_list)}
        user_list = list()
        user_push = user_list.append
        while True:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "lxml")
            for name in soup.select("td.screenname"):
                user = User()
                user.screen_name = name.select_one("a[name]").attrs["name"]
                user.name = name.select_one("strong.fullname").text
                user_push(user)
            ele = soup.select_one("div.w-button-more > a")
            if ele:
                url = f"{self.m_twitter_url}/{ele.attrs['href']}"
            else:
                break
        return user_list
