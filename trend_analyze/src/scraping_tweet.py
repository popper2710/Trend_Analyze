import pickle
import time
import os
import logging
import logging.config
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_binary

from ..config import *


class TwitterScraper:
    def __init__(self, is_headless: bool = True):
        conf_path = PROJECT_ROOT + "config/logging.ini"
        logging.config.fileConfig(conf_path)
        self.logger = logging.getLogger('scraping_tweet')

        options = webdriver.ChromeOptions()
        options.add_argument("--user-agent={}".format(USER_AGENT))
        if is_headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

        if not self._login():
            self.logger.error("Fail to Login twitter")

    def __del__(self):
        self.driver.close()

    # ========================================[public method]=========================================
    def follower_list(self, username: str):
        """
        scraping followers screen name
        :param username: [str] screen name except first "@"
        :return: [list] screen name
        """
        url = f"{TWITTER_DOMAIN}/{username}/followers"

        accounts = set()
        if not self._move_page(url):
            self.logger.error("Fail to move followers page")
            return None

        # scroll page down until can't do it
        while self._scroll():
            account_tags = self.driver.find_elements_by_xpath('//div[@dir="ltr"]')
            for tag in account_tags:
                print(tag.text)
                accounts.add(tag.text)

        return accounts

    def following_list(self, username: str):
        """
        scraping following screen name
        :param username: [str] scrren name except first "@"
        :return: [list] screen name
        """
        url = f"{TWITTER_DOMAIN}/{username}/following"
        accounts = set()
        if not self._move_page(url):
            self.logger.error("Fail to move following page")
            return None

        # scroll page down until can't do it
        while self._scroll():
            account_tags = self.driver.find_elements_by_xpath('//div[@dir="ltr"]')
            for tag in account_tags:
                print(tag.text)
                accounts.add(tag.text)

        return accounts

    # ========================================[private method]========================================
    def _scroll(self):
        """
        page scroll down
        :return:  [bool] Success(True) or Failure(False)
        """
        html_before = self.driver.page_source
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        html_after = self.driver.page_source
        return html_before != html_after

    def _move_page(self, url: str):
        """
        move page with get method
        if redirect happens, return False
        :param url: [str] destination url
        :return:  [bool] Success(True) or Failure(False)
        """
        self.driver.get(url)
        # fail to move follower list page
        return self.driver.current_url == url

    def _login(self):
        """
        logging in twitter
        :return:  [bool] Success(True) or Failure(False)
        """
        f_url = "https://google.com"

        home_url = TWITTER_DOMAIN + "/home"
        cookie_path = PROJECT_ROOT + "config/cookie.pkl"

        self.driver.get(f_url)
        if os.path.isfile(cookie_path):
            with open(cookie_path, "rb") as f:
                cookies = pickle.load(f)
                for c in cookies:
                    if 'expiry' in c:
                        del c['expiry']
                    self.driver.add_cookie(c)

        # if can't login with cookie
        if not self._move_page(home_url):
            url = TWITTER_DOMAIN + "/login/error?username_or_email=%40"
            self.driver.get(url + TWITTER_EMAIL)
            time.sleep(1)  # load react
            password = TWITTER_PWD
            pwd_form = self.driver.find_elements_by_xpath('//input[@autocapitalize="none"]')[1]
            pwd_form.send_keys(password)
            pwd_form.send_keys(Keys.ENTER)

            # save cookies for next login
            with open(cookie_path, "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)

        return self._move_page(home_url)


if __name__ == '__main__':
    s = TwitterScraper(is_headless=False)
    s.following_list("ahl6AfQyIBdoDci")
