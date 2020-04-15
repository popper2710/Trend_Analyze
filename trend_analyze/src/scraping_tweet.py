import pickle
import time
import os
import logging
import logging.config

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import chromedriver_binary

from trend_analyze.config import *


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
        self.driver.maximize_window()

        if not self._login():
            self.logger.error("Fail to Login twitter")

    def __del__(self):
        self.driver.close()

    # ========================================[public method]=========================================
    def follower_list(self, username: str) -> list:
        """
        scraping followers screen name
        :param username: [str] screen name except first "@"
        :return: [list] screen name
        """
        url = f"{TWITTER_DOMAIN}/{username}/followers"

        return self._collect_account_list(url)

    def following_list(self, username: str) -> list:
        """
        scraping following screen name
        :param username: [str] scrren name except first "@"
        :return: [list] screen name
        """
        url = f"{TWITTER_DOMAIN}/{username}/following"

        return self._collect_account_list(url)

    def name_to_id(self, username: str, limit: int = 10) -> str:
        """
        scraping user id from username
        :param username: [str] scrren name except first "@"
        :param limit: scroll limit
        :return: [str] user id
        """
        user_url = f'{TWITTER_DOMAIN}/{username}'
        if not self._move_page(user_url):
            self.logger.error("Fail to move user page")
            return ""
        e = self.driver.find_elements_by_xpath('//a[starts-with(@href, "/i/connect_people?user_id")]')

        c = 0
        while not e and self._scroll(1.0):
            e = self.driver.find_elements_by_xpath('//a[starts-with(@href, "/i/connect_people?user_id")]')
            if c == limit:
                self.logger.error("can not convert from username to user id")
                return ""
            c += 1

        return e[0].get_attribute("href").split('=')[-1]

    # ========================================[private method]========================================
    def _scroll(self, wait: float = 1.0) -> bool:
        """
        page scroll down
        :param wait: [float] wait time after scroll
        :return: [bool] Success(True) or Failure(False)
        """
        html_before = self.driver.page_source
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait)
        html_after = self.driver.page_source
        return html_before != html_after

    def _move_page(self, url: str, wait: float = 1.0) -> bool:
        """
        move page with get method
        if redirect happens, return False
        :param url: [str] destination url
        :param wait: [float] wait time after move page
        :return:  [bool] Success(True) or Failure(False)
        """
        self.driver.get(url)
        time.sleep(wait)
        # fail to move follower list page
        return self.driver.current_url == url

    def _login(self) -> bool:
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

    def _collect_account_list(self, url: str) -> list:
        """
        collect user name from following or followed list page
        :param url: following or followed list url
        :return: [list] accounts
        """
        if not self._move_page(url):
            self.logger.error("Fail to move list page")
            return []

        start = time.time()
        accounts = set()
        fail_count = 0
        # scroll page down until can't do it
        while self._scroll():
            account_tags = self.driver.find_elements_by_xpath('//div[@dir="ltr"]')
            for tag in account_tags:
                try:
                    accounts.add(tag.text[1:])
                except StaleElementReferenceException:
                    fail_count += 1

        elapsed_time = time.time() - start
        self.logger.info("URL: {}, Success: {}, Failure: {}, Time: {}s".format(url,
                                                                               len(accounts),
                                                                               fail_count,
                                                                               elapsed_time))
        return list(accounts)