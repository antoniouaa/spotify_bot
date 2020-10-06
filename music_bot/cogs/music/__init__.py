from .music import Music


def setup(bot):
    setup_music(bot)


def teardown(bot):
    teardown_music(bot)


def setup_music(bot):
    music = Music(bot)
    bot.add_cog(music)


def teardown_music(bot):
    bot.remove_cog(Music.__name__)