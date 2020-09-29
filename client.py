from spotify_bot import SpotifyBot

import json
import discord
from discord.ext import commands


class SpotifyClient(commands.Cog):
    def __init__(self):
        self.spotify = SpotifyBot()

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello back!")

    @commands.command()
    async def freeze(self, ctx):
        users = [user["display_name"] for user in self.spotify.users]
        out = "Users\n" + "\n".join(users)
        await ctx.send(out)

    @commands.command()
    async def register(self, ctx, *user_info):
        display_name = " ".join(user_info[:-1])
        user_id = user_info[-1]
        if user_id is None or display_name is None:
            await ctx.send("--help\nProper usage:\n$register <id> <display_name>")
            raise discord.ClientException("Improper command usage")
        self.spotify.register_user(user_id, display_name)
        print(f"User registration: {user_id} as {display_name}")
        await ctx.send(f"User {display_name} now registered.")

    @commands.command()
    async def playlist(self, ctx, *playlist_info):
        user, keyword = playlist_info
        if user and keyword:
            (
                pl_id,
                url,
                pl_name,
            ) = self.spotify.get_user_playlist_by_keyword_and_display_name(
                user, keyword
            )
            print(f"Playlist found: {pl_id}")
            pl_embed = discord.Embed(Title="pl_name", description="Playlist request")
            pl_embed.add_field(name="Requested by", value=user, inline=True)
            pl_embed.add_field(name="Link", value=url, inline=True)
            await ctx.send(embed=pl_embed)