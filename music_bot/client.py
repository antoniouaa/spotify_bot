"""
The discord bot's client class
"""

import os
import sys
import logging
from datetime import datetime

import discord
from discord.ext import commands

from .cogs.spotify import Spotify

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, config):
        self.config = config
        self.start_time = datetime.utcnow()
        super().__init__(
            command_prefix=self.config.COMMAND_PREFIX,
            description="music_bot - A music bot for the Kipriakon diskort server",
        )

    @property
    def uptime(self):
        return datetime.utcnow() - self.start_time

    def run_with_token(self):
        if not self.config._TOKEN:
            logger.critical("Token is empty, please add one in the configuration file")
            sys.exit(1)
        try:
            self.run(self.config._TOKEN)
        except discord.errors.LoginFailure:
            logger.critical("Cannot login, bad credentials")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        self.add_cog(Spotify(self.config))
        logger.info("Loaded cog: SpotifyClient")
