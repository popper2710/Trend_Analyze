import os
from datetime import datetime

# constant value
TEST_USER_ID = "999942020238995456"
TEST_USERNAME = 'ZulmIhP1nlMOT5y'
JAPAN_WOEID = 23424856
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\\")
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

TWITTER_DOMAIN = "https://twitter.com"

DEFAULT_USER_ID = "0"
DEFAULT_TWEET_ID = "0"
DEFAULT_CREATED_AT = datetime.fromisoformat("1970-01-01")
DEFAULT_ENTITY_URL = "Default Entity Url"
DEFAULT_HASHTAG = "Default HashTag"
