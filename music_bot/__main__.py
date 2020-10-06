"""
Used to start up the bot and setup logging
"""

import argparse
import time
import sys

from .client import Bot
from .config import Config

from discord.ext import commands


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
        config = Config(args.config_file)
    except IOError as err:
        print("No config file found")
        sys.exit(1)

    bot = Bot(config)

    @bot.command()
    @commands.is_owner()
    async def shutdown(ctx):
        print("Shutting down")
        await ctx.bot.close()

    bot.run_with_token()
