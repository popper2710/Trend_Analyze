import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_binary

from ..config import *


class TwitterScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--user-agent={}".format(USER_AGENT))
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

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
        self.driver.get(home_url)

        # if can't login with cookie
        if self.driver.current_url != home_url:
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

    def __del__(self):
        self.driver.close()

    def follower_list(self, username):
        url = f"{TWITTER_DOMAIN}`/{username}/followers"
        self.driver.get(url)
        if self.driver.current_url != url:
            return None

        html_before = "before"
        html_after = "after"
        # scroll page until can't do it
        while html_before != html_after:
            html_before = self.driver.page_source
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            html_after = self.driver.page_source


if __name__ == '__main__':
    s = TwitterScraper()
    s.follower_list("ahl6AfQyIBdoDci")
