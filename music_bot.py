from client import SpotifyClient

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


@bot.command()
async def reload(ctx):
    bot.remove_cog("SpotifyClient")
    bot.add_cog(SpotifyClient())
    print(f"SpotifyClient cog reloaded!")


bot_token = get_discord_bot_token()
bot.run(bot_token)