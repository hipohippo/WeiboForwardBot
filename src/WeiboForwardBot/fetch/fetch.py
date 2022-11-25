import asyncio
import logging
from typing import List, Tuple, Dict

import httpx
import pandas as pd

from WeiboForwardBot.constant import CARD_URL, HEADERS, CardType, RequestConfig
from WeiboForwardBot.fetch.format import Format
from WeiboForwardBot.fetch.weibo_post import WeiboPost

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_posts_sorted(
    uid_list: List[str], poll_delta: pd.Timedelta, last_visit_time_dict: Dict[str, pd.Timestamp]
) -> List[str]:
    all_posts = []
    for uid in uid_list:
        cutoff_time = max(
            (pd.Timestamp.utcnow() - poll_delta).tz_convert(None),
            last_visit_time_dict.get(uid, pd.Timestamp("2021-01-01")),
        )
        uid_post = await fetch_weibo_from_uid(uid, cutoff_time)
        all_posts += uid_post
    all_posts.sort(key=lambda x: x.post_time)
    return [Format.reformat_html_message(Format.compose_html_message(post)) for post in all_posts]


async def fetch_weibo_from_uid(uid: str, cutoff_time: pd.Timestamp) -> List[WeiboPost]:
    """

    :param uid:
    :param cutoff_time:  tz-naive GMT time
    :return:   all weibo posts from the user (with uid) after cutoff_time
    """
    cards = []
    tasks = []
    posts: List[WeiboPost] = []
    for i in range(RequestConfig.MAX_PAGE):
        tasks.append(asyncio.create_task(fetch_cards_from_user_page(uid, i + 1)))
    for i in range(RequestConfig.MAX_PAGE):
        page_cards, status = await tasks[i]
        cards += page_cards
    for idx, card in enumerate(cards):
        try:
            weibo_post = WeiboPost(card["mblog"])
            if weibo_post.post_time >= cutoff_time and not weibo_post._is_top:
                posts.append(weibo_post)
        except Exception as e:
            logging.info(f"cannot process {uid}, {idx}, {e}")
    return posts


async def fetch_cards_from_user_page(uid: str, page: int) -> Tuple[List[dict], int]:
    await asyncio.sleep(RequestConfig.THROTTLE)
    try:
        response = await httpx.AsyncClient().get(
            CARD_URL, params={"containerid": "230413" + uid, "page": page}, headers=HEADERS
        )
        status_code = response.status_code
        content = response.json()
    except Exception as e:
        logging.info(f"unable to fetch page {page} for user {uid}...{e}")
        return [], 0

    logging.info(f"fetched page {page} for user {uid}....{status_code}")
    if status_code != 200:
        return [], status_code

    cards = content.get("data", {"cards": []}).get("cards", [])
    if len(cards) > 0 and cards[0]["card_type"] == CardType.CARD_GROUP.value:
        all_cards = cards[0]["card_group"] + cards[1:]
    else:
        all_cards = cards
    return [card for card in all_cards if card["card_type"] != CardType.NO_WEIBO.value], status_code


def build_posts(cards: List[dict]) -> List[WeiboPost]:
    # cards, status = fetch_cards_for_user("2336643011", 4)
    all_posts = [WeiboPost(card["mblog"]) for card in cards]
    return all_posts
