import datetime
import unittest
import os

from pyfields.typing_utils import FieldTypeError
from valid8.entry_points import ValidationError

import trend_analyze.src.model as model
from trend_analyze.config import *


class TestUrlModel(unittest.TestCase):
    """
    test class for model/hashtag.py
    """

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_default_value(self):
        hashtag = model.Hashtag()

        self.assertEqual(hashtag.hashtag, DEFAULT_HASHTAG)
        self.assertEqual(hashtag.start, -1)
        self.assertEqual(hashtag.end, -1)
        self.assertEqual(hashtag.created_at, DEFAULT_CREATED_AT)

    def test_type_validate(self):
        hashtag = model.Hashtag()

        test_int = 1
        test_str = "test"

        try:
            hashtag.hashtag = test_str
        except FieldTypeError:
            self.fail("hashtag FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            hashtag.hashtag = test_int

        try:
            hashtag.start = test_int
        except FieldTypeError:
            self.fail("start FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            hashtag.start = test_str
        try:
            hashtag.end = test_int
        except FieldTypeError:
            self.fail("end FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            hashtag.end = test_str
        try:
            hashtag.created_at = datetime.now()
        except FieldTypeError:
            self.fail("created_at FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            hashtag.created_at = test_int

    def test_max_len(self):
        hashtag = model.Hashtag()

        try:
            hashtag.hashtag = "A"
            hashtag.hashtag = "A" * 75
            hashtag.hashtag = "A" * 150
        except ValidationError:
            self.fail("hashtag Validation Error about max length is occurred unexpectedly.")
        with self.assertRaises(ValidationError):
            hashtag.hashtag = "A" * 151

    def test_forbidden_blank(self):
        hashtag = model.Hashtag()
        test_val = str()
        try:
            test_val = "A"
            hashtag.hashtag = test_val
            test_val = "0"
            hashtag.hashtag = test_val
        except ValidationError:
            self.fail("hashtag raised ValidationError about blank unexpectedly\nInput Value: {}".format(test_val))

        with self.assertRaises(ValidationError):
            hashtag.hashtag = ""
        with self.assertRaises(ValidationError):
            hashtag.hashtag = " " * 20
        with self.assertRaises(ValidationError):
            hashtag.hashtag = "    " * 5
