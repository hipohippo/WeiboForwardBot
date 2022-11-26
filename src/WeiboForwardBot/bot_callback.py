import asyncio
import logging
from typing import List

import pandas as pd
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from WeiboForwardBot.fetch.fetch import fetch_posts_sorted
from WeiboForwardBot.fetch.format import Format


async def poll_weibo(context: ContextTypes.DEFAULT_TYPE):
    try:
        uid_list: List[str] = pd.read_excel(context.bot_data["uid_file"])["uid"].drop_duplicates().astype(str).tolist()
        logging.info(str(uid_list))
    except Exception as e:
        logging.error(f"unable to read uid list - {e}")
        return
    posts: List[str] = await fetch_posts_sorted(
        uid_list, context.bot_data["poll_interval"], context.bot_data["last_visit_time_dict"]
    )
    logging.info(f"{len(posts)}")
    for post_html in posts:
        preview_on = Format.preview_on(post_html)
        await asyncio.sleep(context.bot_data["throttleControl"])  ## required otherwise telegram will throttle
        await context.bot.send_message(
            chat_id=context.bot_data["channel_id"],
            text=post_html,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=not preview_on,
        )


async def schedule_job(update, context: ContextTypes.DEFAULT_TYPE):
    # context.job_queue.run_once(poll_weibo, when=0, name="get_weibo_polling", chat_id=update.effective_chat.id)
    # context.job_queue.run_repeating(dummy, interval=60, first=20)
    context.job_queue.run_repeating(
        poll_weibo, interval=int(context.bot_data["poll_interval"] / pd.Timedelta("1 second")), first=5
    )
