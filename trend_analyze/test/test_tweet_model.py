import unittest
import datetime

from pyfields.typing_utils import FieldTypeError
from valid8.entry_points import ValidationError

import trend_analyze.src.model as model
from trend_analyze.config import *


class TestTweetModel(unittest.TestCase):
    """
    test class for model/tweet.py
    """

    def __init__(self, *args, **kwargs):
        super(TestTweetModel, self).__init__(*args, **kwargs)
        self.tweet = model.Tweet()

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_default_value(self):
        """
        [!!] "user" cannot test
        """
        tweet = model.Tweet()
        self.assertEqual(tweet.tweet_id, DEFAULT_TWEET_ID)

        # This statement must fail because cannot get same object.
        # self.assertEqual(tweet.user, model.User)

        self.assertEqual(tweet.text, "")
        self.assertEqual(tweet.lang, "")
        self.assertEqual(tweet.retweet_count, -1)
        self.assertEqual(tweet.favorite_count, -1)
        self.assertEqual(tweet.source, "")
        self.assertEqual(tweet.in_reply_to_status_id, "")
        self.assertEqual(tweet.coordinates, "")
        self.assertEqual(tweet.place, "")
        self.assertEqual(tweet.created_at, DEFAULT_CREATED_AT)
        time_diff = datetime.now() - tweet.updated_at
        self.assertLessEqual(time_diff.seconds, 600)
        self.assertEqual(tweet.hashtags, [])
        self.assertEqual(tweet.urls, [])

    def test_type_validate(self):
        """
        [!!] "hashtags" and "urls" cannot test
        """
        tweet = model.Tweet()

        test_int = 1
        test_str = "Invalid"
        test_user = model.User()

        # tweet_id
        try:
            tweet.tweet_id = test_str
        except ValidationError:
            self.fail("tweet_id Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.tweet_id = test_int

        # user
        try:
            tweet.user = test_user
        except ValidationError:
            self.fail("user Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.user = test_str

        # text
        try:
            tweet.text = test_str
        except ValidationError:
            self.fail("text Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.text = test_int

        # lang
        try:
            tweet.lang = test_str
        except ValidationError:
            self.fail("lang Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.lang = test_int

        # retweet_count
        try:
            tweet.retweet_count = test_int
        except ValidationError:
            self.fail("retweet_count Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.retweet_count = test_str

        # favorite_count
        try:
            tweet.favorite_count = test_int
        except ValidationError:
            self.fail("favorite_count Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.favorite_count = test_str

        # source
        try:
            tweet.source = test_str
        except ValidationError:
            self.fail("source Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.source = test_int

        # in_reply_to_status_id
        try:
            tweet.in_reply_to_status_id = test_str
        except ValidationError:
            self.fail("in_reply_to_status_id Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.in_reply_to_status_id = test_int

        # coordinates
        try:
            tweet.coordinates = test_str
        except ValidationError:
            self.fail("coordinates Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.coordinates = test_int

        # place
        try:
            tweet.place = test_str
        except ValidationError:
            self.fail("place Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.place = test_int

        # created_at
        try:
            tweet.created_at = datetime.now()
        except ValidationError:
            self.fail("created_at Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.created_at = test_str

        # updated_At
        try:
            tweet.updated_at = datetime.now()
        except ValidationError:
            self.fail("updated_at Validation is occurred unexpectedly. ")
        with self.assertRaises(FieldTypeError):
            tweet.updated_at = test_str

    def test_max_len(self):
        tweet = model.Tweet()

        # tweet_id
        try:
            tweet.tweet_id = "A"
            tweet.tweet_id = "A" * 15
            tweet.tweet_id = "A" * 30
        except ValidationError:
            self.fail("tweet_id raised ValidationError about length unexpectedly")

        with self.assertRaises(ValidationError):
            tweet.tweet_id = "A" * 31

        # text
        try:
            tweet.text = "A"
            tweet.text = "A" * 150
            tweet.text = "A" * 300
        except ValidationError:
            self.fail("text raised ValidationError about length unexpectedly")
        with self.assertRaises(ValidationError):
            tweet.text = "A" * 301

        # lang
        try:
            tweet.lang = "A"
            tweet.lang = "A" * 5
            tweet.lang = "A" * 10
        except ValidationError:
            self.fail("lang raised ValidationError about length unexpectedly")
        with self.assertRaises(ValidationError):
            tweet.lang = "A" * 11

        # source
        try:
            tweet.source = "A"
            tweet.source = "A" * 25
            tweet.source = "A" * 50
        except ValidationError:
            self.fail("source raised ValidationError about length unexpectedly")
        with self.assertRaises(ValidationError):
            tweet.source = "A" * 51

    def test_forbidden_blank(self):
        tweet = model.Tweet()
        test_val = str()
        try:
            test_val = "A"
            tweet.tweet_id = test_val
            test_val = "0"
            tweet.tweet_id = test_val
        except ValidationError:
            self.fail("tweet_id raised ValidationError about blank unexpectedly\nInput Value: {}".format(test_val))

        with self.assertRaises(ValidationError):
            tweet.tweet_id = ""
        with self.assertRaises(ValidationError):
            tweet.tweet_id = " " * 20
        with self.assertRaises(ValidationError):
            tweet.tweet_id = "    " * 5
