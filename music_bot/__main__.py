"""
Used to start up the bot and setup logging
"""

import logging
import argparse
import sys

from .client import Bot
from .config import Config


LOG_FILE = "music_bot.log"
LOG_FILE_MODE = "w"
LOG_FORMAT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
LOG_DATE_FORMAT = "[%Y/%m/%d %H:M:%S]"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Music bot for Kipriakon diskort")
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Set logging level to DEBUG",
    )
    parser.add_argument(
        "config_file",
        help="Specify a configuration file",
    )
    return parser.parse_args()


def setup_logger(log_level=logging.INFO):
    log_fmt = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    log_handle = logging.FileHandler(
        filename=LOG_FILE,
        encoding="utf-8",
        mode=LOG_FILE_MODE,
    )
    log_handle.setFormatter(log_fmt)
    logger = logging.getLogger(__name__)
    logger.setLevel(level=log_level)
    logger.addHandler(log_handle)
    return logger


if __name__ == "__main__":
    args = parse_arguments()
    logger = setup_logger(log_level=args.debug)
    try:
        config = Config("config.ini")
    except IOError as err:
        logger.error("Unable to read configuration file", exc_info=err)
        sys.exit(1)

    logger.info("Starting bot")
    bot = Bot(config)
    bot.run_with_token()