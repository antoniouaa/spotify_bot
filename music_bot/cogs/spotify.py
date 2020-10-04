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

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello back!")

    @commands.command(name="freeze", aliases=["list", "show"])
    async def freeze(self, ctx):
        """Lists all users in the database"""
        users = self.db.fetch_all_users()
        names_of_users = [f'{user["user"]}# {user["spotify_id"]}' for user in users]
        out = "Users\n" + "\n".join(names_of_users)
        await ctx.send(out)

    @commands.command(name="register", aliases=["signup"])
    async def register(self, ctx, *user_info):
        """Makes a request to register a new user to the database providing their username and spotify ID"""
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
        confirm = self.db.register_new_user(user_id, display_name)
        print(f"User registration: {user_id} as {display_name}\n{confirm}")
        await ctx.send(f"User {display_name} now registered.")

    @commands.command(name="delete", aliases=["clean"])
    async def delete(self, ctx, name):
        """Makes a request to delete a user by their provided username"""
        if name is None:
            print(f"Error using the command: too few arguments ({ctx.author})")
            raise discord.ClientException("Improper command usage: No name given")
        status = self.db.delete_user_by_display_name(name)
        if status == 204:
            print(f"User {name} was successfully deleted")
            await ctx.send(f"User {name} was successfully deleted from the database")
        elif status == 404:
            print(f"User {name} not found in the database")
            await ctx.send(f"User {name} does not exist")

    @commands.command(name="playlist", aliases=["pl"])
    async def playlist(self, ctx, *playlist_info):
        """Finds a playlist by its name and its owner's username and sends its URL in an embedded message"""
        if len(playlist_info) < 2:
            await ctx.send(
                "--help\nCommand `playlist`:\n\tReturns a link to the spotify playlist requested.\nProper usage:\n\t`$playlist <display name> <playlist name>`"
            )
            raise discord.ClientException("Improper command usage")
        else:
            try:
                user, keyword = playlist_info
            except ValueError as e:
                await ctx.send(str(e))
                await ctx.send(
                    "--help\nCommand `playlist`:\n\tReturns a link to the spotify playlist requested.\nProper usage:\n\t`$playlist <display name> <playlist name>`"
                )
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

    def get_user_playlist_by_keyword_and_display_name(
        self, display_name, playlist_name
    ):
        """Finds a user's ID by their username and then retrieves a playlist's ID by its provided name"""
        user_id = self.db.fetch_userid_by_username(display_name)
        playlist = self.user_playlists(user=user_id, limit=5)
        for items in playlist["items"]:
            if playlist_name.lower() in items["name"].lower():
                id_ = items["id"]
                ext_urls = items["external_urls"]["spotify"]
                return (id_, ext_urls, items["name"])
        raise ValueError("Playlist does not exist")

    #@commands.command(aliases=["play_from", "play_list"])
    async def play_from_playlist(self, ctx, *request_info):
        """Fetches a list of the songs in a playlist, given it's name and its owner's name"""
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
            tracks = self.playlist_items(
                pl_id,
                offset=0,
                fields="items.track.id,items.track.name,items.track.artists,total",
                additional_types=["track"],
            )
            pl_embed = discord.Embed(title="Results", description="Query Results")
            addToQueue=[]
            for track in tracks["items"]:
                name = track["track"]["name"]
                artists = track["track"]["artists"]
                artists_name = " ".join(artist["name"] for artist in artists)
                #await ctx.send(f"adding {name} {artists_name}")
                addToQueue.append(f"{name} - {artists_name}")
                #time.sleep(0.75)
            total = tracks["total"]
            await ctx.send(f"{total} tracks queued!")
            return addToQueue
