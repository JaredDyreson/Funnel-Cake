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

# ME.clone(
# "https://open.spotify.com/playlist/37i9dQZF1E8O1unMNglOfS?si=459ad8d37d744a5e",
# "__messy__",
# )

# ME.merge(
# ["https://open.spotify.com/playlist/4lbM8tXwkbbD5MrDOv1Tx0?si=0fc12b33394d4fea", "https://open.spotify.com/playlist/3UqSygUQ03NdFByKS58gQW?si=e003d2f299e543e6"],
# "My Merged Playlist"
# )

ME.clone("https://open.spotify.com/playlist/4XeWVOEgy8EdlHrPIOBJ0N?si=0d51ecdf73684d37")

# with open("/tmp/notes/LV9hdIKWed1mwV2sfxoUPuuyFw9KjUPs.txt", "r", encoding="utf-8") as fil_ptr:
# # ME.merge(
# # [line.strip("\n") for line in fil_ptr.readlines()],
# # "Coffee Shop Vibes"
# # )
# for line in fil_ptr.readlines():
# print(f"working on: {line}")
# ME.clone(line.strip("\n"))
