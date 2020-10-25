import unittest
import datetime

from pyfields.typing_utils import FieldTypeError
from valid8.entry_points import ValidationError

import trend_analyze.src.model as model
from trend_analyze.config import *


class TestUserModel(unittest.TestCase):
    """
    test class for model/user.py
    """

    def setUp(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = 'test'

    def tearDown(self) -> None:
        os.environ['TREND_ANALYZE_ENV'] = TREND_ANALYZE_ENV

    def test_default_value(self):
        user_relation = model.UserRelation()
        self.assertEqual(user_relation.user_id, DEFAULT_USER_ID)
        self.assertEqual(user_relation.username, DEFAULT_USERNAME)
        self.assertEqual(user_relation.target_id, DEFAULT_USER_ID)
        self.assertEqual(user_relation.target_name, DEFAULT_USERNAME)
        self.assertEqual(user_relation.relation_id, -1)

        # It cannot get same current time, so if time difference is less than 1 seconds, it will pass.
        time_diff = datetime.now() - user_relation.updated_at
        self.assertLessEqual(time_diff.seconds, 600)

    def test_type_validate(self):
        user_relation = model.UserRelation()

        test_int = 1
        test_str = "Invalid Value"
        self.assertIsInstance(user_relation.user_id, str)
        with self.assertRaises(FieldTypeError):
            user_relation.user_id = test_int

        self.assertIsInstance(user_relation.username, str)
        with self.assertRaises(FieldTypeError):
            user_relation.username = test_int

        self.assertIsInstance(user_relation.target_id, str)
        with self.assertRaises(FieldTypeError):
            user_relation.target_id = test_int

        self.assertIsInstance(user_relation.target_name, str)
        with self.assertRaises(FieldTypeError):
            user_relation.target_name = test_int

        self.assertIsInstance(user_relation.relation_id, int)
        with self.assertRaises(FieldTypeError):
            user_relation.relation_id = test_str

        self.assertIsInstance(user_relation.updated_at, datetime)
        with self.assertRaises(FieldTypeError):
            user_relation.updated_at = test_int

    def test_forbidden_blank(self):
        user_relation = model.UserRelation()

        with self.assertRaises(ValidationError):
            user_relation.user_id = ""
        with self.assertRaises(ValidationError):
            user_relation.user_id = " " * 20
        with self.assertRaises(ValidationError):
            user_relation.user_id = "    " * 5

        with self.assertRaises(ValidationError):
            user_relation.target_name = ""
        with self.assertRaises(ValidationError):
            user_relation.target_name = " " * 20
        with self.assertRaises(ValidationError):
            user_relation.target_name = "    " * 5

        with self.assertRaises(ValidationError):
            user_relation.target_id = ""
        with self.assertRaises(ValidationError):
            user_relation.target_id = " " * 20
        with self.assertRaises(ValidationError):
            user_relation.target_id = "    " * 5

        with self.assertRaises(ValidationError):
            user_relation.target_name = ""
        with self.assertRaises(ValidationError):
            user_relation.target_name = " " * 20
        with self.assertRaises(ValidationError):
            user_relation.target_name = "    " * 5

