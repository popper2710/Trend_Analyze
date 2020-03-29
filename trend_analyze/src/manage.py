from .controller import Controller
from .get_data import GetTweetInfo


class Manage:
    def __init__(self):
        self.gti = GetTweetInfo()
        self.controller = Controller()

    def update_trend_availables(self):
        availables = self.gti.get_trends_available()
        self.controller(availables)

    def store_user_tweet(self, user_id):
        pass

