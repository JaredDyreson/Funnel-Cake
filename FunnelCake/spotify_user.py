from FunnelCake.spotify_playlist import Playlist
from FunnelCake.constants import DUMP_LOCATION

from FunnelCake.funnel_cake_exceptions import URLParsingException, TokenExpiredException

from FunnelCake.dataclasses.token import Token

import re
import typing
import pathlib
import json
import base64
import requests
import functools
import operator


class SpotifyUser:
    """
    A class to represent a Spotify user
    """

    def __init__(self, token: Token, url: str):
        if not isinstance(token, Token) and isinstance(url, str):
            raise ValueError

        # FIXME: this is broken
        # if token.expired():
        # raise TokenExpiredException("Current token is expired, please renew")

        self.token = token

        from_user_re = re.compile(r"https://open.spotify.com/user/(?P<user>.*)\?si=.*")

        if not (match := from_user_re.match(url)):
            raise URLParsingException(f"[ERROR] Url {url} does not conform")

        self.user_id = match.group("user")

    def splay(self, results) -> typing.Any:
        """
        Take a response and fully exhaust it
        @param results : API response as a dictionary

        @return typing.List: all results in a list
        """

        container = results["items"]
        while results["next"]:
            results = self.token.elevated_credentials.next(results)
            container.extend(results["items"])
        return container

    def clone(self, url: str, destination: str = "") -> None:
        """Clone a playlist from a url"""

        src_playlist = Playlist.from_url(url, self.token)

        cover_image: typing.Dict = self.token.elevated_credentials.playlist_cover_image(
            src_playlist.meta_data.id_
        )[0]["url"]

        match cover_image:
            case None:
                raise Exception("Could not find playlist cover image")
            case _:
                cover_image = base64.b64encode(requests.get(cover_image).content)

        self.create_playlist(
            name=f"{src_playlist.meta_data.name} | Cloned"
            if not destination
            else destination,
            public=True,
            description=f"Cloned playlist from {src_playlist.url}"
            if not src_playlist.meta_data.description
            else src_playlist.meta_data.description,
            tracks=[element.uri for element in src_playlist.tracks],
            cover_image=cover_image,
        )

    def merge(self, playlists: typing.List[str], destination: str = "") -> None:
        src_playlists = [Playlist.from_url(url, self.token) for url in playlists]

        collated = functools.reduce(operator.add, src_playlists)

        self.create_playlist(
            name=f"Example Merged Playlist" if not destination else destination,
            public=True,
            description=f"Merged playlist from {''.join([playlist.meta_data.name for playlist in src_playlists])}",
            tracks=[element.uri for element in collated],
        )

    def add_tracks(self, playlist_id: str, tracks: typing.List[str]) -> None:
        """Add all the tracks in a list to a given playlust"""

        for x in range(0, len(tracks), 100):
            self.token.elevated_credentials.playlist_add_items(
                playlist_id, tracks[x : x + 100]
            )

    def create_playlist(
        self,
        name: str,
        public: bool = True,
        description: str = "",
        tracks: typing.List[str] = [],
        cover_image=None,
    ) -> None:
        """
        Create a playlist for the current user
        NOTE: This does not check if you have already created the playlist

        @param name : name of the playlist
        @param public : is it visible to the public
        @param description : small description about the playlist
        @param tracks : list of tracks to fill if given
        @param cover_image : base64 encoded image to give to the API

        @return None : the function will make an API call and the user should see it populate
        """

        response = self.token.elevated_credentials.user_playlist_create(
            self.user_id, name, public, False, description
        )

        if tracks and response is not None:
            self.add_tracks(response["id"], tracks)
        if cover_image and response is not None:
            self.token.elevated_credentials.playlist_upload_cover_image(
                response["id"], cover_image
            )

    def obtain_playlists(self) -> typing.Dict[str, str]:
        """
        Get all the playlist of the current user

        @return typing.Dict[str, str] : list of playlist urls
        """

        api_response = self.token.elevated_credentials.current_user_playlists()

        return {
            element["name"]: element["external_urls"]["spotify"]
            for element in self.splay(api_response)
        }

    def obtain_saved_tracks(self) -> typing.Dict[str, typing.Any]:
        """Get all user tracks with the date added"""

        api_response = self.token.elevated_credentials.current_user_saved_tracks()

        return {
            element["track"]["id"]: {"added": element["added_at"]}
            for element in self.splay(api_response)
        }

    def dump(self):
        """
        Dump all meaningful information about the user to disk
        to migrate to another account
        """

        BASE_DIR = pathlib.Path(f"{DUMP_LOCATION}/{self.user_id}")
        directories = ["user_saved_tracks", "playlists", "followers", "following"]
        for directory in directories:
            new_path = pathlib.Path(f"{BASE_DIR}/{directory}")
            if not new_path.is_dir():
                new_path.mkdir(parents=True)
