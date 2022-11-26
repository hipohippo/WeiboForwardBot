import logging
import os
from configparser import ConfigParser

import pandas as pd
from telegram.ext import ApplicationBuilder, CommandHandler

from WeiboForwardBot.bot_callback import schedule_job

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    config = ConfigParser()
    config.read("../../../weibo_forward_bot.ini")
    config = config["weibo_forward_bot"]

    application = ApplicationBuilder().token(config["token"]).build()
    application.bot_data["channel_id"] = int(config["channel_id"])
    application.bot_data["uid_file"] = os.path.join(os.path.dirname(__file__), config["uid_file"])
    application.bot_data["poll_interval"] = pd.Timedelta(f"{config['poll_interval']} min")
    application.bot_data["publish_throttle"] = float(config["publish_throttle"])  ## 0.1s
    application.bot_data["last_visit_time_dict"] = {}

    application.add_handler(CommandHandler("refresh", schedule_job))
    application.run_polling()

    """
    TODO
    1. preview 
    2. image link
    3. parse incoming weibo status
    """
