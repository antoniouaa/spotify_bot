"""
Used to start up the bot and setup logging
"""

import argparse
import sys

from .client import Bot
from .config import Config


def parse_arguments():
    parser = argparse.ArgumentParser(description="Music bot for Kipriakon diskort")
    parser.add_argument(
        "config_file",
        help="Specify a configuration file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    try:
        config = Config("config.ini")
    except IOError as err:
        print("No config file found")
        sys.exit(1)

    bot = Bot(config)
    bot.run_with_token()
