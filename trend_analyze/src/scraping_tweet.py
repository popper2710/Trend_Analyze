import pickle
import time
import logging
import logging.config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

from trend_analyze.config import *



class TwitterScraper:
    """
    This class collects tweet data that the packages cannot collect. This is slow and unstable,
    so you should use TweetFetcher class as far as possible.
    """

    def __init__(self):
        logging.config.dictConfig(LOGGING_DICT_CONFIG)
        self.logger = logging.getLogger('scraping_tweet')

        options = Options()
        options.add_argument("--user-agent={}".format(USER_AGENT))
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        self.twi_email = TWITTER_EMAIL
        self.twi_pass = TWITTER_PWD
        self.driver = webdriver.Chrome(options=options)

    def __enter__(self):
        self.driver.maximize_window()
        if not self._login():
            self.logger.error("Fail to Login twitter")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        self.driver.quit()

    # ========================================[public method]=========================================
    def name_to_id(self, username: str) -> (str, None):
        """
        convert username to user id
        :param username: screen name except first "@"
        :type username: str
        :return: str or None
        """
        url = f"{TWITTER_DOMAIN}/{username}"
        if self._move_page(url, wait=0.3):
            css_selector = "div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > img"
            for c in self.driver.find_elements_by_css_selector(css_selector):
                elements = c.get_attribute("src").split("/")
                if elements[3] == "profile_banners":
                    return elements[4]
        return None

    def id_to_name(self, user_id: str) -> (str, None):
        """
        convert user id to name
        :param user_id:
        :type user_id: str
        :return: str or None
        """
        url = f"{TWITTER_DOMAIN}/i/user/{user_id}"
        self._move_page(url, wait=0.3)
        username = self.driver.current_url.split("/")[3]
        if username != "i":
            return username
        else:
            return None

    def follower_list(self, username: str) -> list:
        """
        scraping followers screen username
        :param username: screen username except first "@"
        :type username: str
        :return: [list] screen username
        """
        url = f"{TWITTER_DOMAIN}/{username}/followers"

        return self._collect_account_list(url)

    def following_list(self, username: str) -> list:
        """
        scraping following screen username
        :param username: scrren username except first "@"
        :type username: str
        :return: [list] screen username
        """
        url = f"{TWITTER_DOMAIN}/{username}/following"

        return self._collect_account_list(url)

    # ========================================[private method]========================================
    def _scroll(self, wait: float = 1.0) -> bool:
        """
        page scroll down
        :param wait: wait time after scroll
        :type wait: float
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
        [!!] if redirect happens, return False
        :param url: destination url
        :type url: str
        :param wait: wait time after move page
        :type wait: float
        :return:  [bool] Success(True) or Failure(False)
        """
        self.driver.get(url)
        time.sleep(wait)
        # fail to move follower list page
        return self.driver.current_url == url

    def _login(self, cookie_cache=True) -> bool:
        """
        logging in twitter
        :return:  [bool] Success(True) or Failure(False)
        """
        f_url = "https://google.com"

        home_url = TWITTER_DOMAIN + "/home"
        cookie_path = PROJECT_ROOT + "config/cookie.pkl"

        self.driver.get(f_url)
        if os.path.isfile(cookie_path) and cookie_cache:
            with open(cookie_path, "rb") as f:
                cookies = pickle.load(f)
                for c in cookies:
                    if 'expiry' in c:
                        del c['expiry']
                    self.driver.add_cookie(c)

        # if can't login with cookie
        if not self._move_page(home_url, wait=0.0):
            url = TWITTER_DOMAIN + "/login/error?username_or_email=%40"
            self.driver.get(url + self.twi_email)
            time.sleep(1)  # load react
            password = self.twi_pass
            pwd_form = self.driver.find_elements_by_xpath('//input[@autocapitalize="none"]')[1]
            pwd_form.send_keys(password)
            pwd_form.send_keys(Keys.ENTER)

            # save cookies for next login
            if cookie_cache:
                with open(cookie_path, "wb") as f:
                    pickle.dump(self.driver.get_cookies(), f)

        return self._move_page(home_url, wait=0.5)

    def _collect_account_list(self, url: str) -> list:
        """
        collect user username from following or followed list page
        :param url: following or followed list url
        :type url: str
        :return: [list] accounts
        """
        if not self._move_page(url, 0.0):
            self.logger.error("Fail to move list page")
            return []

        start = time.time()
        accounts = set()
        fail_count = 0
        # scroll page down until can't do it
        while True:
            account_tags = self.driver.find_elements_by_xpath('//div[@dir="ltr"]')
            for tag in account_tags:
                try:
                    accounts.add(tag.text[1:])
                except StaleElementReferenceException:
                    fail_count += 1
            if not self._scroll(0.5):
                break

        elapsed_time = time.time() - start
        self.logger.info("URL: {}, Success: {}, Failure: {}, Time: {}s".format(url,
                                                                               len(accounts),
                                                                               fail_count,
                                                                               elapsed_time))
        return list(accounts)
