from enum import Enum

INDEX_API_LINK = "http://m.weibo.cn/api/container/getIndex"

LOGIN_URL = "https://passport.weibo.cn/sso/login"
CARD_URL = "https://m.weibo.cn/api/container/getIndex?"
HEADERS = {
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
}


class PageType(Enum):
    ARTICLE = "ARTICLE"
    VIDEO = "VIDEO"
    OTHER = "OTHER"  ## can be places but will ignore here


class CardType(Enum):
    CARD_GROUP = 11
    SINGLE_CARD = 9
    NO_WEIBO = 58


class WeiboPostType(Enum):
    ORIGINAL = "ORIGINAL"
    RETWEET = "RETWEET"


class LongWeiboProperty(Enum):
    NOT_LONG = "NOT_LONG"
    LONG_WEIBO = "LONG_WEIBO"
    LONG_PIC = "LONG_PIC"


class WeiboContentProperty(Enum):
    TEXT = "TEXT"
    PIC = "PIC"
    VIDEO = "VIDEO"
    ARTICLE = "ARTICLE"


class RequestConfig:
    THROTTLE = 1.5  # second
    MAX_PAGE = 3
