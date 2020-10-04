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
        del self.bot

    def test_client_cogs(self):
        self.assertEqual(self.bot._cogs, ["spotify", "music"])

    def test_client_exception(self):
        self.assertRaises(discord.errors.LoginFailure, self.bot.run_with_token())
