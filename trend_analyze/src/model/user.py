from pyfields import field

from trend_analyze.src.validate import Validate
from trend_analyze.config.define import *


class User:
    v = Validate().generate

    user_id: str = field(default=DEFAULT_USER_ID, validators=v(is_blank=True, max_len=30), check_type=True)
    name: str = field(default="", validators=v(max_len=100), check_type=True)
    screen_name: str = field(default="", validators=v(max_len=50), check_type=True)
    location: str = field(default="", validators=v(max_len=50), check_type=True)
    description: str = field(default="", validators=v(max_len=300), check_type=True)
    followers_count: int = field(default=-1, check_type=True)
    following_count: int = field(default=-1, check_type=True)
    listed_count: int = field(default=-1, check_type=True)
    favorites_count: int = field(default=-1, check_type=True)
    statuses_count: int = field(default=-1, check_type=True)
    created_at: datetime = field(default=DEFAULT_CREATED_AT, check_type=True)
    updated_at: datetime = field(default=datetime.now(), check_type=True)

    def to_vec(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "screen_name": self.screen_name,
            "location": self.location,
            "description": self.description,
            "followers_count": self.followers_count,
            "following_count": self.following_count,
            "listed_count": self.listed_count,
            "favorites_count": self.favorites_count,
            "statuses_count": self.statuses_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

