import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import discord
from discord.ext import commands

from ..db import DB
from .music import Music


class Spotify(commands.Cog, spotipy.Spotify):
    def __init__(self, config):
        self.db_config = (
            config.MONGO_USERNAME,
            config.MONGO_PASSWORD,
            config.MONGO_DBNAME,
        )
        self.db = DB(*self.db_config)
        self.spotify_id = config._SPOTIFY_CLIENT_ID
        self.spotify_secret = config._SPOTIFY_CLIENT_SECRET
        super(Spotify, self).__init__(
            auth_manager=SpotifyClientCredentials(
                client_id=self.spotify_id, client_secret=self.spotify_secret
            )
        )

    # TODO: fix this function
    def get_user_playlist_by_keyword_and_display_name(
        self, display_name, playlist_name
    ):
        user = self.get_user_id(display_name)
        playlist = self.user_playlists(user=user, limit=10)
        for items in playlist["items"]:
            if playlist_name.lower() in items["name"].lower():
                id = items["id"]
                ext_urls = items["external_urls"]["spotify"]
                return (id, ext_urls, items["name"])
        raise ValueError("Playlist does not exist")

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello back!")

    @commands.command(name="freeze", aliases=["list", "show"])
    async def freeze(self, ctx):
        users = self.db.fetch_all_users()
        names_of_users = [f'{user["user"]}# {user["spotify_id"]}' for user in users]
        out = "Users\n" + "\n".join(names_of_users)
        await ctx.send(out)

    @commands.command(name="register", aliases=["signup"])
    async def register(self, ctx, *user_info):
        if len(user_info) < 2:
            print(f"Error using the command: too few arguments ({ctx.author})")
            raise discord.ClientException("Improper command usage")
        display_name = " ".join(user_info[:-1])
        user_id = user_info[-1]
        if user_id is None or display_name is None:
            await ctx.send(
                "--help\nProper usage:\n$register <spotify id> <display name>"
            )
            raise discord.ClientException("Improper command usage: too few arguments")
        confirm = self.db._test_user_creation(user_id, display_name)
        print(f"User registration: {user_id} as {display_name}\n{confirm}")
        await ctx.send(f"User {display_name} now registered.")

    @commands.command()
    async def playlist(self, ctx, *playlist_info):
        if len(playlist_info) != 2:
            await ctx.send(
                "--help\nCommand `playlist`:\n\tReturns a link to the spotify playlist requested.\nProper usage:\n\t`$playlist <display name> <playlist name>`"
            )
            raise discord.ClientException("Improper command usage")
        else:
            try:
                user, keyword = playlist_info
                (
                    pl_id,
                    url,
                    pl_name,
                ) = self.get_user_playlist_by_keyword_and_display_name(user, keyword)
                print(f"Playlist found: {pl_id}")
                pl_embed = discord.Embed(Title=pl_name, description="Playlist request")
                pl_embed.add_field(name="Requested by", value=user, inline=True)
                pl_embed.add_field(name="Link", value=url, inline=True)
                await ctx.send(embed=pl_embed)
            except ValueError as e:
                await ctx.send(str(e))
                await ctx.send(
                    "--help\nCommand `playlist`:\n\tReturns a link to the spotify playlist requested.\nProper usage:\n\t`$playlist <display name> <playlist name>`"
                )

    @commands.command(aliases=["play_from", "play_list"])
    async def play_from_playlist(self, ctx, *request_info):
        if len(request_info) != 2:
            await ctx.send(
                "--help\nCommand `play_from`:\n\tPlays songs from the spotify playlist requested.\nProper usage:\n\t`$play_from <display name> <playlist name>`"
            )
            raise discord.ClientException("Improper command usage")
        else:
            user, keyword = request_info
            (
                pl_id,
                url,
                npl_name,
            ) = self.get_user_playlist_by_keyword_and_display_name(user, keyword)
            tracks = self.spotify.playlist_items(
                pl_id,
                offset=0,
                fields="items.track.id,items.track.name,items.track.artists,total",
                additional_types=["track"],
            )
            pl_embed = discord.Embed(title="Results", description="Query Results")
            for track in tracks["items"]:
                name = track["track"]["name"]
                artists = track["track"]["artists"]
                artists_name = " ".join(artist["name"] for artist in artists)
                # await ctx.send(f"!play {name} {artists_name}")
                Music.yt(f"{name} - {artists_name}")
                time.sleep(0.75)
            total = tracks["total"]
            await ctx.send(f"{total} tracks queued!")
