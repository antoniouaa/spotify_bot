import os
import sys
import logging
import configparser

from .errors import ConfigurationError

log = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file):
        self.config_sections = ["CREDENTIALS", "PERMISSIONS", "CHAT"]
        self.config_file = config_file
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file, encoding="utf-8")
        if not self.config_sections == config.sections():
            raise ConfigurationError(
                "One or more required Configuration sections are missing\n"
                "Check your Configuration file",
            )

        self._TOKEN = config.get("CREDENTIALS", "TOKEN")
        self._SPOTIFY_CLIENT_ID = config.get("CREDENTIALS", "SPOTIFY_CLIENT_ID")
        self._SPOTIFY_CLIENT_SECRET = config.get("CREDENTIALS", "SPOTIFY_CLIENT_SECRET")
        self.MONGO_USERNAME = config.get("CREDENTIALS", "MONGO_USERNAME")
        self.MONGO_PASSWORD = config.get("CREDENTIALS", "MONGO_PASSWORD")
        self.MONGO_DBNAME = config.get("CREDENTIALS", "MONGO_DBNAME")

        self.OWNER_ID = config.get("PERMISSIONS", "OWNER_ID")

        self.BOT_ID = config.get("CHAT", "BOT_ID")
        self.COMMAND_PREFIX = config.get("CHAT", "COMMAND_PREFIX")
        self.BOUND_CHANNELS = config.get("CHAT", "BIND_TO_CHANNELS")
