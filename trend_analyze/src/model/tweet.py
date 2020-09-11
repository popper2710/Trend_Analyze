from typing import List

from pyfields import field

from trend_analyze.src.model.user import User
from trend_analyze.src.model.hashtag import Hashtag
from trend_analyze.src.model.entity_url import EntityUrl
from trend_analyze.src.validate import Validate
from trend_analyze.config import *


class Tweet:
    v = Validate().generate

    tweet_id: str = field(default=DEFAULT_TWEET_ID, validators=v(is_blank=True, max_len=30), check_type=True)
    user: User = field(default=User(), check_type=True)
    text: str = field(default="", validators=v(max_len=300), check_type=True)
    lang: str = field(default="", validators=v(max_len=10), check_type=True)
    retweet_count: int = field(default=-1, check_type=True)
    favorite_count: int = field(default=-1, check_type=True)
    source: str = field(default="", validators=v(max_len=50), check_type=True)
    in_reply_to_status_id: str = field(default="", validators=v(max_len=30), check_type=True)
    coordinates: str = field(default="", check_type=True)
    place: str = field(default="", check_type=True)
    created_at: datetime = field(default=DEFAULT_CREATED_AT, check_type=True)
    updated_at: datetime = field(default=datetime.now(), check_type=True)
    hashtags: List[Hashtag] = field(default=[], check_type=True)
    urls: List[EntityUrl] = field(default=[], check_type=True)
    is_official: bool = field(default=False, check_type=True)
