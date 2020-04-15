import unittest
import datetime

from pyfields.typing_utils import FieldTypeError
from valid8.entry_points import ValidationError

import trend_analyze.src.model as model
from trend_analyze.config import *


class TestUserModel(unittest.TestCase):
    """
    test class for some class under model directory
    """

    def test_default_value(self):
        user = model.User()
        self.assertEqual(user.user_id, DEFAULT_USER_ID)
        self.assertEqual(user.name, "")
        self.assertEqual(user.screen_name, "")
        self.assertEqual(user.location, "")
        self.assertEqual(user.description, "")
        self.assertEqual(user.followers_count, -1)
        self.assertEqual(user.following_count, -1)
        self.assertEqual(user.listed_count, -1)
        self.assertEqual(user.favorites_count, -1)
        self.assertEqual(user.statuses_count, -1)
        self.assertEqual(user.created_at, DEFAULT_CREATED_AT)

        # It cannot get same current time, so if time difference is less than 1 seconds, it will pass.
        time_diff = datetime.now() - user.updated_at
        self.assertLessEqual(time_diff.seconds, 30)

    def test_type_validate(self):
        user = model.User()

        self.assertIsInstance(user.user_id, str)
        with self.assertRaises(FieldTypeError):
            user.user_id = 1

        self.assertIsInstance(user.name, str)
        with self.assertRaises(FieldTypeError):
            user.name = 1

        self.assertIsInstance(user.screen_name, str)
        with self.assertRaises(FieldTypeError):
            user.screen_name = 1

        self.assertIsInstance(user.location, str)
        with self.assertRaises(FieldTypeError):
            user.location = 1

        self.assertIsInstance(user.description, str)
        with self.assertRaises(FieldTypeError):
            user.description = 1

        self.assertIsInstance(user.followers_count, int)
        with self.assertRaises(FieldTypeError):
            user.followers_count = "Invalid Value"

        self.assertIsInstance(user.following_count, int)
        with self.assertRaises(FieldTypeError):
            user.following_count = "Invalid Value"

        self.assertIsInstance(user.listed_count, int)
        with self.assertRaises(FieldTypeError):
            user.listed_count = "Invalid Value"

        self.assertIsInstance(user.favorites_count, int)
        with self.assertRaises(FieldTypeError):
            user.favorites_count = "Invalid Value"

        self.assertIsInstance(user.statuses_count, int)
        with self.assertRaises(FieldTypeError):
            user.statuses_count = "Invalid Value"

        self.assertIsInstance(user.created_at, datetime)
        with self.assertRaises(FieldTypeError):
            user.created_at = 0

        self.assertIsInstance(user.updated_at, datetime)
        with self.assertRaises(FieldTypeError):
            user.updated_at = 0

    def test_max_len(self):
        user = model.User()

        # max length is 30
        try:
            user.user_id = "A"
            user.user_id = "A" * 15
            user.user_id = "A" * 30
        except ValidationError:
            self.fail("user_id raised ValidationError about length unexpectedly")

        with self.assertRaises(ValidationError):
            user.user_id = "A" * 31

        # max length is 100
        try:
            user.name = "A"
            user.name = "A" * 50
            user.name = "A" * 100
        except ValidationError:
            self.fail("name raised ValidationError about length unexpectedly")

        with self.assertRaises(ValidationError):
            user.name = "A" * 101

        # max length is 50
        try:
            user.screen_name = "A"
            user.screen_name = "A" * 25
            user.screen_name = "A" * 50
        except ValidationError:
            self.fail("screen_name raised ValidationError about length unexpectedly")

        with self.assertRaises(ValidationError):
            user.screen_name = "A" * 51

        # max length is 50
        try:
            user.location = "A"
            user.location = "A" * 25
            user.location = "A" * 50
        except ValidationError:
            self.fail("location raised ValidationError about max length unexpectedly")

        with self.assertRaises(ValidationError):
            user.location = "A" * 51

        # max length is 300
        try:
            user.description = "A"
            user.description = "A" * 150
            user.description = "A" * 300
        except ValidationError:
            self.fail("description raised ValidationError about length unexpectedly")

        with self.assertRaises(ValidationError):
            user.description = "A" * 301

    def test_forbidden_blank(self):
        user = model.User()
        test_val = ""
        try:
            test_val = "A"
            user.user_id = test_val
            test_val = "0"
            user.user_id = test_val
        except ValidationError:
            self.fail("user_id raised ValidationError about blank unexpectedly\nInput Value: {}".format(test_val))

        with self.assertRaises(ValidationError):
            user.user_id = ""
        with self.assertRaises(ValidationError):
            user.user_id = " " * 20
        with self.assertRaises(ValidationError):
            user.user_id = "    " * 5
