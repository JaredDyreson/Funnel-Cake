"""
Module that contains a class to search for
specific qualities in a Spotify playlist
"""

from FunnelCake.SpotifyPlaylist import SpotifyPlaylist

import typing
import json
import requests


class PlaylistFilter:
    """
    Apply filters on a playlist to extract
    specific qualities
    """

    def __init__(self, playlist: SpotifyPlaylist):
        self.playlist = playlist
        self.detailed_information = []

    def obtain_information(self) -> typing.List:
        """
        Get a detailed read out of the playlist

        @return typing.List : response from Spotify
        """

        container = []
        for index in range(0, len(self.playlist.tracks), 50):
            _slice = self.playlist.tracks[index : index + 50]

            params = (
                ("ids", ",".join(_slice)),
                ("market", "ES"),
            )

            response = requests.get(
                "https://api.spotify.com/v1/tracks",
                headers=self.playlist.manager.headers,
                params=params,
            )
            # container |= json.loads(response.text)["tracks"]
            container.append(json.loads(response.text)["tracks"])

        return container

    def explicit(self) -> typing.List[str]:
        """
        Find all songs that are explicit in a given playlist
        """

        return list(
            filter(lambda x: x["explicit"] == "true", self.detailed_information)
        )

    def clean(self) -> typing.List[str]:
        """
        Find all songs that are explicit in a given playlist
        """

        return list(
            filter(lambda x: x["explicit"] == "false", self.detailed_information)
        )
