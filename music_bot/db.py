import pymongo


class DB:
    def __init__(self, username, password, db_name):
        self.username = username
        self.password = password
        self.db_name = db_name
        self.db = pymongo.MongoClient(
            f"mongodb+srv://{self.username}:{self.password}@cluster0.y6mfx.mongodb.net/{self.db_name}?retryWrites=true&w=majority"
        )

    def _test_user_creation(self, id, name):
        inserted_doc = self.db.test.users.insert_one({"spotify_id": id, "user": name})
        return inserted_doc