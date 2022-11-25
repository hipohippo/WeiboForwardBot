# class for a single weibo post - can be original or retweeted
from typing import List

import pandas as pd

from WeiboForwardBot.constant import PageType


class WeiboPost:
    def __init__(self, mblog: dict):
        """

        :param original_mblog: content_json = cards[2]["mblog"], original weibo
        mblog must be original?
        """
        if "retweeted_status" in mblog:
            self.is_retweet = True
            original_mblog = mblog["retweeted_status"]
        else:
            self.is_retweet = False
            original_mblog = mblog

        # original or retweeted

        if original_mblog.get("user"):
            self._author_id: int = original_mblog.get("user").get(
                "id", -1
            )  # id/screen_name not available if original post was deleted
            self._author_name: str = original_mblog.get("user").get("screen_name", "NA")
        else:
            self._author_id, self._author_name = -1, "NA"

        self._html_text: str = original_mblog.get("text", "")  # if you jsonfy it, it will be encoded in utf-8
        self._pic_num: int = original_mblog.get("pic_num", 0)
        self.pic_size = "large"
        self._pic_link: List[str] = [
            self.get_page_pic_url(pic, self.pic_size) for pic in original_mblog.get("pics", [])
        ]  # can be empty if pic_num=0. and is incomplete if pic_num>9, should be handled as long (picture) weibo
        self._is_long_text: bool = bool(int(original_mblog.get("isLongText", False)))
        self._long_text = None
        self._original_created_time: pd.Timestamp = pd.Timestamp(original_mblog.get("created_at")).tz_convert(None)
        self._original_post_id: str = original_mblog.get("id", "-1")
        self._original_post_link: str = f"https://m.weibo.cn/status/{self._original_post_id}" if self._original_post_id != "-1" else None
        self._is_top: bool = bool(int(original_mblog.get("isTop", 0)))

        self._has_page: bool = "page_info" in original_mblog  # if weibo has article or video
        if self._has_page:
            page_info = original_mblog["page_info"]
            self._page_type: PageType = {"article": PageType.ARTICLE, "video": PageType.VIDEO}.get(
                page_info["type"], PageType.OTHER
            )
            self._page_url: str = page_info["page_url"]
            self._page_content_abstract: str = page_info.get("page_title", "") + page_info.get(
                "content1", ""
            ) + page_info.get("content2", "")
        else:
            self._page_type = None

        if self.is_retweet:
            self._retweet_post_id: str = mblog["id"]
            self._retweet_post_link: str = f"https://m.weibo.cn/status/{self._retweet_post_id}"
            self._retweet_author_id: str = mblog["user"]["id"]
            self._retweet_author_name: str = mblog["user"]["screen_name"]
            self._retweet_comment: str = mblog.get("text")
            self._retweet_time: pd.Timestamp = pd.Timestamp(mblog.get("created_at")).tz_convert(None)

    def __str__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def get_page_pic_url(url_json: dict, pic_size: str):
        if pic_size == "large" and "large" in url_json:
            return url_json["large"]["url"]
        else:
            return url_json["url"]

    @property
    def post_time(self) -> pd.Timestamp:
        if self.is_retweet:
            return self._retweet_time
        else:
            return self._original_created_time
