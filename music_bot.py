from client import SpotifyClient
from music_client import Music

import json
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="$")


def get_discord_bot_token(filename="credentials.json"):
    with open(filename) as creds_f:
        creds = json.loads(creds_f.read())
        return creds["DISCORD_BOT_TOKEN"]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_cog(SpotifyClient())
    bot.add_cog(Music(bot))


@bot.command()
async def reload(ctx):
    bot.remove_cog("SpotifyClient")
    bot.remove_cog("MusicClient")
    bot.add_cog(SpotifyClient())
    bot.add_cog(Music(bot))
    print(f"cogs reloaded!")

bot_token = get_discord_bot_token()
bot.run(bot_token)