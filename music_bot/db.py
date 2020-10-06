import pymongo
from bson.son import SON

from .errors import DataBaseError


class DB:
    def __init__(self, username, password, db_name):
        self.username = username
        self.password = password
        self.db_name = db_name
        self.client = pymongo.MongoClient(
            f"mongodb+srv://{self.username}:{self.password}@cluster0.y6mfx.mongodb.net/{self.db_name}?retryWrites=true&w=majority"
        )
        self.db = self.client[db_name]

    def close(self):
        self.client.close()

    def register_new_user(self, id, name):
        """Registers a new user"""
        user = {"spotify_id": id, "user": name.lower()}
        if self.db.users.find_one(user):
            raise DataBaseError("User already exists")
        inserted_doc = self.db.users.insert_one(user)
        return inserted_doc

    def fetch_userid_by_username(self, name):
        """Fetches a user's ID by their username"""
        raw_user = self.db.users.find_one({"user": name.lower()})
        user = raw_user["spotify_id"]
        return user

    def fetch_all_users(self):
        """Fetches all usernames and IDs"""
        raw_users = list(self.db.users.find({}))
        fields = ("spotify_id", "user")
        users = [{field: raw_user[field] for field in fields} for raw_user in raw_users]
        return users

    def delete_user_by_display_name(self, name):
        """Deletes a user if they exist by their username"""
        if bool(self.db.users.find_one({"user": name.lower()})):
            self.db.users.delete_one({"user": name})
            return 204
        return 404
