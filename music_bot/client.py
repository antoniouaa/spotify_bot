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
        self.add_cog(Music(self))
        print("Loaded cog: Music")
        self.add_cog(Spotify(self.config))
        print("Loaded cog: Spotify")
        

    @commands.command()
    async def reload(self):
        self.remove_cog("SpotifyClient")
        self.remove_cog("MusicClient")
        self.add_cog(Spotify(self.config))
        self.add_cog(Music(self))
        print(f"cogs reloaded!")
