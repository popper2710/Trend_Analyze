import pickle, random, string, copy
from typing import List

from trend_analyze.config import *
from trend_analyze.src.model import *
from trend_analyze.src.controller import Controller
from trend_analyze.src.fetch_data import TwitterFetcher
from trend_analyze.src.fetch_data_from_api import ApiTwitterFetcher

USERS_SAMPLE_NAME = "users_sample.pkl"
TWEETS_SAMPLE_NAME = "tweets_sample.pkl"
USER_RELATIONS_SAMPLE_NAME = "user_relations_sample.pkl"


class Sample:
    def __init__(self):
        self.controller = Controller()
        self.tf = TwitterFetcher()
        self.atf = ApiTwitterFetcher()
        self._users_sample = self.__load_sample(USERS_SAMPLE_NAME)
        self._tweets_sample = self.__load_sample(TWEETS_SAMPLE_NAME)
        self._user_relations_sample = self.__load_sample(USER_RELATIONS_SAMPLE_NAME)

    def users_sample(self) -> List[User]:
        if not self._users_sample:
            self.update_users_sample()
        return self._users_sample

    def tweets_sample(self) -> List[Tweet]:
        if not self._tweets_sample:
            self.update_tweets_sample()
        return self._tweets_sample

    def user_relations_sample(self) -> List[UserRelation]:
        if not self._user_relations_sample:
            self.update_user_relations_sample()
        return self._user_relations_sample

    def update_all(self) -> None:
        self.update_users_sample()
        self.update_tweets_sample()
        self.update_user_relations_sample()

    def update_tweets_sample(self, size: int = 20, use_api: bool = True) -> bool:
        try:
            if size <= 0:
                print(f"Bad size: {size}")
            elif size <= 5:
                print("[WARNING!!] Sample size is very small. It may not be enough to use for test")

            org_tweet = next(self.atf.fetch_user_tweet(TEST_USER_ID, count=1))[0] if use_api \
                else self.tf.fetch_tweet(TEST_USER_ID, max_tweet=1)[0]
            tweets = [copy.deepcopy(org_tweet) for _ in range(size)]
            for i in range(1, size):
                tweets[i].tweet_id = ''.join(random.choices(string.digits, k=19))
                tweets[i].text = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0, 140)))
                tweets[i].user = random.choice(self._users_sample)

            self._tweets_sample = tweets
            with open("sample/" + TWEETS_SAMPLE_NAME, "wb") as f:
                pickle.dump(tweets, f)
            return True

        except Exception as e:
            print(e)
            return False

    def update_users_sample(self, size: int = 20) -> bool:
        try:
            if size <= 0:
                print(f"Bad size: {size}")
            elif size <= 5:
                print("[WARNING!!] Sample size is very small. It may not be enough to use for test")

            org_user = self.atf.fetch_user_info(TEST_USER_ID)
            users = [copy.deepcopy(org_user) for _ in range(size)]
            for i in range(1, size):
                users[i].user_id = ''.join(random.choices(string.digits, k=random.randint(1, 25)))

            self._users_sample = users
            with open("sample/" + USERS_SAMPLE_NAME, "wb") as f:
                pickle.dump(users, f)

            return True

        except Exception as e:
            print(e)
            return False

    def update_user_relations_sample(self, size: int = 20) -> bool:
        try:
            if size <= 0:
                print(f"Bad size: {size}")
            elif size <= 5:
                print("[WARNING!!] Sample size is very small. It may not be enough to use for test")
            org_user_relations = self.atf.fetch_user_relations(TEST_USERNAME)
            self._user_relations_sample = org_user_relations

            with open("sample/" + USER_RELATIONS_SAMPLE_NAME, "wb") as f:
                pickle.dump(org_user_relations, f)

            return True

        except Exception as e:
            print(e)
            return False

    @staticmethod
    def __load_sample(filename: str):
        if os.path.isfile("sample/" + filename):
            with open("sample/" + filename, "rb") as f:
                return pickle.load(f)
        else:
            return None


if __name__ == '__main__':
    sample = Sample()
    sample.update_all()
