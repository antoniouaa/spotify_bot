import asyncio

import discord
import youtube_dl

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
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = bot
        self.sp = sp
        self.playQueue = []

    @commands.command(name="join", aliases=["here", "voice"])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    async def queueSong(self, keywords):
        self.playQueue.append(keywords)

    async def playYT(self, ctx):
        print(f"<{', '.join(self.playQueue)}>")

        def ytNext(e):
            if self.playQueue:
                self.playQueue.pop(0)
                asyncio.run_coroutine_threadsafe(self.playYT(ctx), self.loop)

        async with ctx.typing():
            if self.playQueue:
                player = await YTDLSource.from_url(
                    self.playQueue[0], loop=self.bot.loop
                )
                ctx.voice_client.play(player, after=ytNext)
                await ctx.send(f"Now playing: {player.title}")
            else:
                await ctx.send(f"Playlist empty")

    @commands.command(name="play_spotify", aliases=["play_from"])
    async def play_spotify(self, ctx, *args):
        q = await self.sp.play_from_playlist(ctx, args[0], args[1])
        embedVar = discord.Embed(
            title="Added Playlist", description="Playlist info", color=0x00FF00
        )
        for i, s in enumerate(q):
            embedVar.add_field(name=f"{i}.", value=s, inline=True)
        await ctx.send(embed=embedVar)
        await ctx.send(f"Adding {len(q)} songs to queue")
        self.playQueue = self.playQueue + q
        if not ctx.voice_client.is_playing():
            await self.playYT(ctx)

    @commands.command(name="yt", aliases=["youtube", "play"])
    async def yt(self, ctx, *, url):
        """Queries youtube using the terms given and plays back the first result"""
        await ctx.send(f"Adding {url} to queue")
        print(f"Song requested: {url}")
        await self.queueSong(url)
        if not ctx.voice_client.is_playing():
            await self.playYT(ctx)

    @commands.command(name="skip", aliases=["next"])
    async def skip(self, ctx):
        ctx.voice_client.stop()
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
