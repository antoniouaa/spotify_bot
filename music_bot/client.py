"""
The discord bot's client class
"""

import os
import sys
from datetime import datetime

import discord
from discord.ext import commands

from .cogs.music.music import Music
from .cogs.spotify.spotify import Spotify


class Bot(commands.Bot):
    def __init__(self, config):
        self.config = config
        self.start_time = datetime.utcnow()
        self.available_cogs = {"spotify": None, "music": None}
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
        sp = Spotify(self)
        mu = Music(self, sp)
        await self.change_presence(
            activity=discord.Activity(
                name="Spotify",
                type="3",
                state="Listening",
                details="Come request a song from me!",
            )
        )
        self.available_cogs.update({"spotify": sp, "music": mu})
        for name, c in self.available_cogs.items():
            self.add_cog(c)
        print("All cogs successfully loaded")
