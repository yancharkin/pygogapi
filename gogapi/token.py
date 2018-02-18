import sys
import requests
import json
import pytz
from datetime import datetime, timedelta

if sys.version_info[0] == 2:
    import time
    from urllib import quote as urlquote
    def create_timestamp(dt):
        timestamp = int(time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0)
        return timestamp
elif sys.version_info[0] == 3:
    from urllib.parse import quote as urlquote
    def create_timestamp(dt):
        timestamp = int(dt.timestamp())
        return timestamp

from gogapi.base import ApiError
from gogapi import urls

CLIENT_ID = "46899977096215655"
CLIENT_SECRET = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"

REDIRECT_URL = "https://embed.gog.com/on_login_success?origin=client"


def get_auth_url():
    redirect_url_quoted = urlquote(REDIRECT_URL)
    return urls.galaxy(
        "auth", client_id=CLIENT_ID, redir_uri=redirect_url_quoted)


class Token:
    def set_data(self, token_data):
        if "error" in token_data:
            raise ApiError(token_data["error"], token_data["error_description"])

        self.access_token = token_data["access_token"]
        self.refresh_token = token_data["refresh_token"]
        self.expires_in = timedelta(seconds=token_data["expires_in"])
        self.scope = token_data["scope"]
        self.session_id = token_data["session_id"]
        self.token_type = token_data["token_type"]
        self.user_id = token_data["user_id"]
        if "created" in token_data:
            self.created = datetime.fromtimestamp(
                token_data["created"], pytz.utc)
        else:
            self.created = datetime.now(pytz.utc)

    def get_data(self):
        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_in": int(self.expires_in.total_seconds()),
            "scope": self.scope,
            "session_id": self.session_id,
            "token_type": self.token_type,
            "user_id": self.user_id,
            "created": create_timestamp(self.created)
        }
        return token_data

    def __repr__(self):
        return str(self.__dict__)

    def load(self, filename):
        with open(filename, "r") as f:
            self.set_data(json.load(f))

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.get_data(), f, indent=2, sort_keys=True)

    # FIX Have no idea what I'm doing, but it works (for now) in boty python 2 & 3 :)
    #def from_file(filename):
    @classmethod
    def from_file(*args):
        filename = args[1]
        token = Token()
        token.load(filename)
        return token

    #def from_code(login_code):
    @classmethod
    def from_code(*args):
        login_code = args[1]
        token_query = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": login_code,
            "redirect_uri": REDIRECT_URL # Needed for origin verification
        }
        token_resp = requests.get(urls.galaxy("token"), params=token_query)
        token = Token()
        token.set_data(token_resp.json())
        return token

    def refresh(self):
        token_query = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        token_resp = requests.get(urls.galaxy("token"), params=token_query)
        self.set_data(token_resp.json())

    def expired(self, margin=timedelta(seconds=60)):
        expires_at = self.created + self.expires_in
        return (datetime.now(pytz.utc) - expires_at) > margin
