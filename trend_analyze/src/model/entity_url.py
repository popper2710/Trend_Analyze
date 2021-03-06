from pyfields import field

from trend_analyze.src.validate import Validate
from trend_analyze.config import *


class EntityUrl:
    v = Validate().generate

    url: str = field(default=DEFAULT_ENTITY_URL, validators=v(is_blank=True, max_len=150), check_type=True)
    start: int = field(default=-1, check_type=True)
    end: int = field(default=-1, check_type=True)
    expanded_url: str = field(default="", validators=v(max_len=2083), check_type=True)
    created_at: datetime = field(default=DEFAULT_CREATED_AT, check_type=True)

    def to_vec(self) -> dict:
        return {
            "url": self.url,
            "start": self.start,
            "end": self.end,
            "expanded_url": self.expanded_url,
            "created_at": self.created_at,
        }
