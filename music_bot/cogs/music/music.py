import asyncio

import discord
import youtube_dl
import os, glob

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(f"ytsearch: {url}", download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot, sp):
        # Bot handle
        self.bot = bot

        # Spotify handle
        self.sp = sp

        # Song queue
        self.playQueue = []

        # Make cache dir
        try:
            os.mkdir("cache/")
        except OSError:
            print(
                "Creation of the cache directory failed (already exists or insufficient priviledges)"
            )
        else:
            print("Successfully created the cache directory")
        os.chdir("cache/")

    async def queueSong(self, keywords):
        """Adds the keywords string to the song queue"""
        self.playQueue.append(keywords)

    async def playYT(self, ctx):
        """Plays the first song in the song queue"""

        def ytNext(e):
            """Removes the first song and plays the next one"""

            def purge(pat):
                """deletes all files mathcing pat glob from the current working dir"""
                for f in glob.glob(pat):
                    print("deleting " + str(os.path.join(os.getcwd(), f)))
                    os.remove(os.path.join(os.getcwd(), f))

            if self.playQueue:
                self.playQueue.pop(0)
                asyncio.run_coroutine_threadsafe(self.playYT(ctx), self.bot.loop)
                # Clean up cache. If errors occur duting skip etc, this is the first place to look for a fix
                purge("youtube*")

        async with ctx.typing():
            if self.playQueue:
                player = await YTDLSource.from_url(
                    self.playQueue[0], loop=self.bot.loop
                )
                ctx.voice_client.play(player, after=ytNext)
                await ctx.send(f"Now playing: {player.title}")
            else:
                await ctx.send(f"Playlist empty")

    @commands.command(name="join", aliases=["here", "voice"])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins the command issuer's voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command(name="play_spotify", aliases=["play_from"])
    async def play_spotify(self, ctx, *args):
        """Adds the songs from the provided spotify playlist to the queue"""
        # Get the song names using the spotify cog
        q = await self.sp.play_from_playlist(ctx, args[0], args[1])

        # Gather playlist info into an embed to output
        embedVar = discord.Embed(
            title="Playlist Queued", description="Playlist info", color=0x00FF00
        )
        for i, (song, album, url) in enumerate(q[:3], start=1):
            embedVar.add_field(
                name=f"{i}) Song Name and Artist", value=f"{song}", inline=True
            )
            embedVar.add_field(name="Album", value=album, inline=True)
            embedVar.add_field(name="URL", value=url, inline=True)
        await ctx.send(embed=embedVar)
        await ctx.send(f"Adding {len(q)} songs to queue")
        song_list = [song for song, _, _ in q]

        # Append the playlist to the queue
        self.playQueue = self.playQueue + song_list

        # Start playing if not already playing something
        if not ctx.voice_client.is_playing():
            await self.playYT(ctx)

    @commands.command(name="yt", aliases=["youtube", "play"])
    async def yt(self, ctx, *, url):
        """Queries youtube using the terms given and plays back the first result"""
        await ctx.send(f"Adding {url} to queue")

        # Append the song to the queue
        await self.queueSong(url)

        # Start playing if not already playing something
        if not ctx.voice_client.is_playing():
            await self.playYT(ctx)

    @commands.command(name="skip", aliases=["next"])
    async def skip(self, ctx):
        """Skips the currently playing song and plays the next one"""
        # Force interrupt the play function (ctx.voice_client.play)
        ctx.voice_client.stop()

        # Play the next song
        await self.playYT(ctx)

    @commands.command(name="volume", aliases=["level", "vol"])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(name="stop", aliases=["kill", "silence"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        self.playQueue = []
        await ctx.voice_client.disconnect()

    @yt.before_invoke
    @play_spotify.before_invoke
    async def ensure_voice(self, ctx):
        """Makes sure the bot is connected to a voice channel"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
