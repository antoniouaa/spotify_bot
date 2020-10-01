import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pprint
import json


class SpotifyBot(spotipy.Spotify):
    def __init__(self):
        self.client_id, self.client_secret = self._get_client_creds()
        super(SpotifyBot, self).__init__(
            auth_manager=SpotifyClientCredentials(
                client_id=self.client_id, client_secret=self.client_secret
            )
        )
        self.users = self._get_users()
    
    # This function gets the users
    def _get_users(self):
        with open("users.json") as users_f:
            return json.loads(users_f.read())["users"]

    def _get_client_creds(self):
        with open("credentials.json") as creds_f:
            creds = json.loads(creds_f.read())
            return creds["SPOTIFY_CLIENT_ID"], creds["SPOTIFY_CLIENT_SECRET"]

    def register_user(self, user_id, display_name):
        self.users.append({"id": user_id, "display_name": display_name.title()})
        with open("users.json", "w") as users_f:
            users = {"users": self.users}
            users_f.write(json.dumps(users))

    def get_user_id(self, display_name):
        for user in self.users:
            if display_name.lower() in user["display_name"].lower():
                return str(user["id"])
        raise ValueError("User not found")

    def get_user_playlist_by_keyword_and_display_name(
        self, display_name, playlist_name
    ):
        user = self.get_user_id(display_name)
        playlist = self.user_playlists(user=user, limit=10)
        for items in playlist["items"]:
            if playlist_name.lower() in items["name"].lower():
                id = items["id"]
                ext_urls = items["external_urls"]["spotify"]
                return (id, ext_urls, items["name"])
        raise ValueError("Playlist does not exist")


sp = SpotifyBot()
# id_, ext_url = sp.get_user_playlist_by_keyword_and_display_name("alex", "newrock")
# sp.register_user(user_id="eriksofs", display_name="Erik Sophocleous")
