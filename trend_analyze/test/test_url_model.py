import unittest
import datetime

from pyfields.typing_utils import FieldTypeError
from valid8.entry_points import ValidationError

import trend_analyze.src.model as model
from trend_analyze.config import *


class TestUrlModel(unittest.TestCase):
    """
    test class for model/entity_url.py
    """

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_default_value(self):
        url = model.EntityUrl()

        self.assertEqual(url.url, DEFAULT_ENTITY_URL)
        self.assertEqual(url.start, -1)
        self.assertEqual(url.end, -1)
        self.assertEqual(url.expanded_url, "")
        self.assertEqual(url.created_at, DEFAULT_CREATED_AT)

    def test_type_validate(self):
        url = model.EntityUrl()

        test_int = 1
        test_str = "test"

        try:
            url.url = test_str
        except FieldTypeError:
            self.fail("url FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            url.url = test_int

        try:
            url.start = test_int
        except FieldTypeError:
            self.fail("start FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            url.start = test_str
        try:
            url.end = test_int
        except FieldTypeError:
            self.fail("end FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            url.end = test_str

        try:
            url.created_at = datetime.now()
            try:
                url.expanded_url = test_str
            except FieldTypeError:
                self.fail("expanded_url FieldTypeError is occurred unexpectedly")

            with self.assertRaises(FieldTypeError):
                url.expanded_url = test_int

        except FieldTypeError:
            self.fail("created_at FieldTypeError is occurred unexpectedly")

        with self.assertRaises(FieldTypeError):
            url.created_at = test_int

    def test_max_len(self):
        url = model.EntityUrl()

        try:
            url.url = "A"
            url.url = "A" * 75
            url.url = "A" * 150
        except ValidationError:
            self.fail("url Validation Error about max length is occurred unexpectedly.")
        with self.assertRaises(ValidationError):
            url.url = "A" * 151

    def test_forbidden_blank(self):
        url = model.EntityUrl()
        test_val = str()
        try:
            test_val = "A"
            url.url = test_val
            test_val = "0"
            url.url = test_val
        except ValidationError:
            self.fail("url raised ValidationError about blank unexpectedly\nInput Value: {}".format(test_val))

        with self.assertRaises(ValidationError):
            url.url = ""
        with self.assertRaises(ValidationError):
            url.url = " " * 20
        with self.assertRaises(ValidationError):
            url.url = "    " * 5
