from get_data import GetTweetInfo
from db import session
import model
import time


class Controller:
    def __init__(self):
        self.session = session
        self.gti = GetTweetInfo()

    def update_trend_available(self):
        """
        update table with current trend available location
        :return: None
        """
        availables = self.gti.get_trends_available()
        items = list()
        append = items.append

        # initialize trend available table
        self.session.execute("DELETE FROM {}".format(model.TrendAvailable.__tablename__))

        for available in availables:
            item = dict()
            item['name'] = available['name']
            item['url'] = available['url']
            item['country'] = available['country']
            item['woeid'] = available['woeid']
            item['countrycode'] = available['countryCode']
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            append(item)

        self.session.execute(model.TrendAvailable.__table__.insert(), items)
        self.session.commit()


def main():
    pass


if __name__ == '__main__':
    update_trend_available()

