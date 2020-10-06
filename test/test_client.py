import unittest

import discord

from music_bot.client import Bot
from music_bot.config import Config

TEST_CONFIG_FILE = ".\\test\\test_config.ini"


class TestClient(unittest.TestCase):
    def setUp(self):
        self.config = Config(config_file=TEST_CONFIG_FILE)
        self.bot = Bot(self.config)

    def tearDown(self):
        del self.config
        self.bot.logout()
        del self.bot

    def test_client_exception(self):
        self.assertRaises(discord.errors.LoginFailure, self.bot.run_with_token())

    def test_client_reads_cog_names(self):
        expected = ["spotify", "music"]
        self.assertEqual(expected, list(self.bot.available_cogs.keys()))
