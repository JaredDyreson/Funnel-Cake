"""Driver code for Funnel Cake"""

import datetime
import pathlib

from pprint import pprint as pp

from FunnelCake.dataclasses.token import Token
from FunnelCake.spotify_user import SpotifyUser
from FunnelCake.spotify_playlist import Playlist

TOKEN = Token(
    pathlib.Path("/home/jared/Projects/SpotifyAuthenticator/credentials.json"),
)

ME = SpotifyUser(TOKEN, "https://open.spotify.com/user/12164553253?si=5af2cdb1739744f6")

ME.clone(
    "https://open.spotify.com/playlist/4IeI5PQYePhXaezV9HRDIr?si=0ee5a49e39404fae",
    "my playlist cloned",
)
