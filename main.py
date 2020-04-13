from trend_analyze.src import Manage
import logging.config


def main():
    manage = Manage()
    TEST_USER_ID = "999942020238995456"
    manage.update_trend_availables()
    manage.store_tweet_including_trend(rank=1)



if __name__ == '__main__':
    main()
