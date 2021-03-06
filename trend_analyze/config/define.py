import os
from datetime import datetime
import logging.handlers

# constant value
JAPAN_WOEID = 23424856
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

TWITTER_DOMAIN = "https://twitter.com"

DEFAULT_USER_ID = "0"
DEFAULT_TWEET_ID = "0"
DEFAULT_USERNAME = "i"
DEFAULT_CREATED_AT = datetime.fromisoformat("1970-01-01")
DEFAULT_ENTITY_URL = "Default Entity Url"
DEFAULT_HASHTAG = "Default HashTag"

ONLY_FOLLOWING_ID = 0
ONLY_FOLLOWED_ID = 1
BIDIRECTIONAL_ID = 2

TWEET_FETCH_LIMIT = 1_000_000_000  # you can change fetching times unlimited, by setting "-1"

TREND_ANALYZE_ENV = "development"

# for logging
LOGGING_DICT_CONFIG = {
    'version': 1,
    'formatters': {
        'customFormat': {
            'format': '[%(asctime)s] %(module)s.py:%(lineno)s %(levelname)s -> %(message)s'

        },
        'csvFormat': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'fileHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'customFormat',
            'filename': PROJECT_ROOT + 'log/root.log'
        },
        'stderrHandler': {
            'class': 'logging.StreamHandler',
            'formatter': 'customFormat',
            'stream': 'ext://sys.stdout'
        },
        'scrapingHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'customFormat',
            'filename': PROJECT_ROOT + 'log/scraping_tweet.log'
        },
        'csvHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'csvFormat',
            'filename': PROJECT_ROOT + 'log/collect_trend_time.csv'
        }
    },
    'root': {
        'handlers': ['fileHandler', 'stderrHandler'],
        'level': logging.DEBUG
    },
    'loggers': {
        'controller': {
            'handlers': ['fileHandler', 'stderrHandler'],
            'level': logging.DEBUG,
            'qualname': 'controller',
            'propagate': 0
        },
        'get_data': {
            'handlers': ['fileHandler', 'stderrHandler'],
            'level': logging.DEBUG,
            'qualname': 'get_data',
            'propagate': 0
        },
        'manage': {
            'handlers': ['stderrHandler'],
            'level': logging.INFO,
            'qualname': 'manage',
            'propagate': 0
        },
        'csv': {
            'handlers': ['csvHandler'],
            'level': logging.INFO,
            'qualname': 'csv',
            'propagate': 0
        },
        'scraping_tweet': {
            'handlers': ['scrapingHandler', 'stderrHandler'],
            'level': logging.DEBUG,
            'qualname': 'scraping_tweet',
            'propagate': 0
        }
    }
}
