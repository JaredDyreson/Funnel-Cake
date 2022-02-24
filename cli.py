"""
Command line tool for interacting with
the Spotify API
"""

"""
Commands:

- specify
    - prompts for url
- append
    - take in new tracks from command lie
        - from_url
        - from_list (comma separated)
        - from_file
            - can contain list of tracks
            - can contain list of links that must become a list of tracks

"""

import pathlib
import dataclasses
import typing

from FunnelCake.dataclasses.token import Token
from FunnelCake.spotify_playlist import Playlist
from FunnelCake.spotify_user import SpotifyUser
from FunnelCake.utils import parse_url

from FunnelCake.funnel_cake_exceptions import URLParsingException

TOKEN = Token(
    pathlib.Path("/home/jared/Projects/SpotifyAuthenticator/credentials.json"),
)


ME = SpotifyUser(TOKEN, "https://open.spotify.com/user/12164553253?si=5af2cdb1739744f6")
container = []


def game_loop():
    CURRENT_PLAYLIST = Playlist.from_url(
        "https://open.spotify.com/playlist/6ropIwtV9pcTon1ukSKMCZ?si=a551e8bb2d004e9d",
        TOKEN,
    )
    while True:
        try:
            command = input(">>> ")
        except (KeyboardInterrupt, EOFError):
            break

        match command:
            case "apply":
                ME.append(CURRENT_PLAYLIST.url, container)
            case "dry":
                print(container)
            case "dupes":
                ME.token.elevated_credentials.playlist_remove_specific_occurrences_of_items(
                    CURRENT_PLAYLIST.meta_data.id_, ME.dupes(CURRENT_PLAYLIST.url)
                )

            case "append":
                source = input("[SRC] >>> ")
                try:
                    parse_url(source)
                    container.extend(
                        [e.uri for e in Playlist.from_url(source, TOKEN).tracks]
                    )
                except URLParsingException:
                    print("Invalid URL")

            case "specify":
                url = input("[URL] >>> ")

                if url:
                    CURRENT_PLAYLIST = Playlist.from_url(url, TOKEN)

            case "clone":
                source = input("[SRC] >>> ")
                name = input("[DEST] >>> ")

                try:
                    parse_url(source)
                    ME.clone(source, name)
                except URLParsingException:
                    print("Invalid URL")

            case "quit":
                break
            case _:
                print(f"Hello {command}")


game_loop()
