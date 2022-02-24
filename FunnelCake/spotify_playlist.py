"""Module for the Spotify playlist"""

import datetime
import json
import pathlib
import requests
import typing

from FunnelCake.dataclasses.playlist_metadata import PlaylistMetaData
from FunnelCake.dataclasses.track import Artist, Track
from FunnelCake.funnel_cake_exceptions import TokenExpiredException
from FunnelCake.dataclasses.token import Token


def parse_response_contents(contents: typing.List[typing.Dict]) -> typing.List[Track]:
    """Take in a dictionary of information and parse it into a list of tracks"""

    return [
        Track(
            [Artist(uri["name"], uri["uri"]) for uri in element["track"]["artists"]],
            element["track"]["duration_ms"],
            element["track"]["explicit"],
            element["track"]["name"],
            element["track"]["popularity"],
            datetime.datetime.strptime("1970-01-01", "%Y-%m-%d"),
            # datetime.datetime.strptime(element["track"]["album"]["release_date"], "%Y-%m-%d"),
            element["track"]["uri"],
        )
        for element in contents
    ]


class Playlist:
    """
    This class is to test the logic of the Playlist class
    without having to spam the API
    """

    def __init__(
        self,
        contents: typing.Dict,
        tracks: typing.List[Track],
        token: Token,
        url=None,
    ):
        self.contents = contents
        self.tracks = tracks
        self.url = url
        self.token = token  # passed from the user to the playlist to obtain information

        self.meta_data = PlaylistMetaData(self.contents, self.url)

    @classmethod
    def from_file(cls, path: typing.Union[pathlib.Path, typing.Text], token: Token):
        """
        FIXME: Broken
        Read in a json file for debugging so you
        do not have to constantly ping the API

        @return cls : class instance that is read in from a file
        """

        with open(path, "r", encoding="utf-8") as fil_ptr:
            contents = json.loads(fil_ptr.read())
            return cls(contents, parse_response_contents(contents), token, "")

    # return cls(headers, contents, tracks)

    @classmethod
    def from_url(cls, url: str, token: Token):
        """
        Obtain information about a given playlist from
        the API directly

        @param headers : allows for API requests to be made, contains the token
        @param url : link to the Spotify playlist

        @return cls : class instance of the playlist
        """

        __returnable = cls({}, [], token, url)

        results = __returnable.token.non_elevated_credentials.playlist_items(
            playlist_id=__returnable.meta_data.id_, 
            fields="total,name,items"
        )

        # results = __returnable.token.non_elevated_credentials.user_playlist_tracks(
        # __returnable.meta_data.id_,
        # fields="total,limit"
        # )

        container = results["items"]


        while len(container) < results["total"]:
            results = __returnable.token.non_elevated_credentials.playlist_items(
                playlist_id=__returnable.meta_data.id_, fields="total,name,items", offset=len(container)
            )
            container.extend(results["items"])

        __returnable.tracks = parse_response_contents(container)

        __returnable.contents = results

        __returnable.meta_data = PlaylistMetaData(__returnable.contents, url)
        return __returnable

    def __add__(self, rhs) -> typing.List[Track]:
        """
        Merge both lists into a dictionary, preserving the
        order of insertion

        @param rhs: other side of the '+' operator

        @return typing.List[str] : combined list of tracks, with no duplicates
        """

        return list(dict.fromkeys(self.tracks + rhs.tracks).keys())

    def __sub__(self, rhs) -> typing.List[Track]:
        """
        Find the intersection of both lists
        This does not preserve the order in which they occur

        @return typing.List[str] : remove all tracks that are in common between the tracks
        """

        return list(set(self.tracks) - set(rhs.tracks))

    def sort_inplace(self, criteria: typing.Callable, reverse: bool) -> None:
        """Sort the container in place using a lambda expression"""

        self.tracks.sort(key=criteria, reverse=reverse)

    def sort_copy(self, criteria: typing.Callable, reverse: bool) -> typing.List[Track]:
        """Sort the container and return a copy using a lambda expression"""

        return sorted(self.tracks, key=criteria, reverse=reverse)

    @property
    def duration(self) -> int:
        """
        See how long the playlist is in milliseconds

        @return int : duration of the playlist
        """

        return sum(track.duration for track in self.tracks)

    @property
    def explicit(self) -> typing.List[Track]:
        """
        Find all the explicit tracks in a given playlist
        """

        return list(filter(lambda x: bool(x.explicit), self.tracks))
