import unittest
import configparser
from copy import deepcopy

from music_bot.db import DB
from music_bot.errors import DataBaseError

TEST_CONFIG_FILE = ".\\test\\test_config.ini"
CONFIG_FILE = "config.ini"

SAMPLE_USERS = [
    {
        "spotify_id": "eriksofs",
        "user": "erik",
    },
    {
        "spotify_id": "1234567890",
        "user": "alex",
    },
    {
        "spotify_id": "sjevans",
        "user": "sarah",
    },
]


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.sample_users = deepcopy(SAMPLE_USERS)
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)
        self.db_config = (
            self.config.get("CREDENTIALS", "MONGO_USERNAME"),
            self.config.get("CREDENTIALS", "MONGO_PASSWORD"),
            "test",
        )
        self.db = DB(*self.db_config)
        self.test_db = self.db.client["test"]
        self.test_collection = self.test_db["users"]
        status_code = self.add_sample_users()
        self.assertEqual(3, len(status_code))

    def add_sample_users(self):
        self.test_collection.delete_many({})
        ids = self.test_collection.insert_many(self.sample_users).inserted_ids
        return ids

    def tearDown(self):
        self.db.close()
        del self.sample_users
        del self.config
        del self.db
        del self.test_db
        del self.test_collection

    def test_db_database_names(self):
        expected = ["music_bot", "test", "admin", "local"]
        database_names = self.db.client.list_database_names()
        self.assertEqual(expected, database_names)

    def test_db_collection_names(self):
        expected = ["users"]
        collection_names = self.test_db.list_collection_names()
        self.assertEqual(expected, collection_names)

    def test_db_fetch_all_users(self):
        users = self.db.fetch_all_users()
        self.assertEqual(SAMPLE_USERS, users)

    def test_db_register_new_user(self):
        test_id = "test_registration"
        test_username = "test_new_user"
        test_user = {
            "spotify_id": test_id,
            "user": test_username,
        }
        SAMPLE_USERS.append(test_user)
        inserted = self.db.register_new_user(test_id, test_username).inserted_id
        self.assertTrue(inserted)
        users = self.db.fetch_all_users()
        self.assertEqual(SAMPLE_USERS, users)

    def test_db_fetch_userid_by_name(self):
        expected = "sjevans"
        actual = self.db.fetch_userid_by_username("sarah")
        self.assertEqual(expected, actual)

    def test_db_register_existing_user(self):
        test_id = "1234567890"
        test_username = "alex"
        with self.assertRaises(DataBaseError):
            self.db.register_new_user(test_id, test_username)
