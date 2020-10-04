"""
The discord bot's client class
"""

import os
import sys
from datetime import datetime

import discord
from discord.ext import commands

from .cogs.spotify import Spotify
from .cogs.music import Music


class Bot(commands.Bot):
    def __init__(self, config):
        self.config = config
        self.start_time = datetime.utcnow()
        self.cogs_ = ["spotify", "music"]
        super().__init__(
            command_prefix=self.config.COMMAND_PREFIX,
            description="music_bot - A music bot for the Kipriakon diskort server",
        )
        

    def run_with_token(self):
        if not self.config._TOKEN:
            print("No token provided in the config file")
            sys.exit(1)
        try:
            self.run(self.config._TOKEN)
        except discord.errors.LoginFailure:
            print("Invalid token provided")

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        spotify = Spotify(self.config)
        self.add_cog(spotify)
        print("Loaded cog: Spotify")
        music = Music(self,spotify)
        self.add_cog(music)
        print("Loaded cog: Music")
