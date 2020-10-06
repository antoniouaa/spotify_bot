from .spotify import Spotify


def setup(bot):
    spotify = Spotify(bot)
    bot.add_cog(spotify)


def teardown(bot):
    bot.remove_cog(Spotify.__name__)