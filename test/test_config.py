import unittest

from music_bot.config import Config

TEST_CONFIG_FILE = ".\\test\\test_config.ini"
SECTIONS = ["CREDENTIALS", "PERMISSIONS", "CHAT"]


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config(config_file=TEST_CONFIG_FILE)

    def tearDown(self):
        del self.config

    def test_config_sections(self):
        sections = ["CREDENTIALS", "PERMISSIONS", "CHAT"]
        self.assertEqual(SECTIONS, self.config.config_sections)

    def test_config_credentials(self):
        self.assertEqual("bot_token", self.config._TOKEN)
        self.assertEqual("spotify_client_id", self.config._SPOTIFY_CLIENT_ID)
        self.assertEqual("spotify_client_secret", self.config._SPOTIFY_CLIENT_SECRET)
        self.assertEqual("mongo_username", self.config.MONGO_USERNAME)
        self.assertEqual("mongo_password", self.config.MONGO_PASSWORD)
        self.assertEqual("mongo_db_name", self.config.MONGO_DBNAME)

    def test_config_permissions(self):
        self.assertEqual("auto", self.config.OWNER_ID)

    def test_config_chat(self):
        self.assertEqual("bot_id", self.config.BOT_ID)
        self.assertEqual("prefix", self.config.COMMAND_PREFIX)
        self.assertEqual("1234567890", self.config.BOUND_CHANNELS)
