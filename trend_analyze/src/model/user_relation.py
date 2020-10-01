from pyfields import field

from trend_analyze.src.validate import Validate
from trend_analyze.config.define import *


class UserRelation:
    v = Validate().generate

    user_id: str = field(default=DEFAULT_USER_ID, validators=v(is_blank=True, max_len=30), check_type=True)
    username: str = field(default=DEFAULT_USERNAME, validators=v(is_blank=True), check_type=True)
    target_id: str = field(default=DEFAULT_USER_ID, validators=v(is_blank=True, max_len=30), check_type=True)
    target_name: str = field(default=DEFAULT_USERNAME, validators=v(is_blank=True), check_type=True)
    relation_id: int = field(default=-1, validators=v(is_blank=True), check_type=True)
    updated_at: datetime = field(default=datetime.now(), check_type=True)

    def to_vec(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "relation_id": self.relation_id,
            "updated_at": self.updated_at,
        }

