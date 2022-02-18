import json
import dataclasses
import datetime
import typing
import pathlib
import re
import requests


@dataclasses.dataclass
class Artist:
    name: str
    uri: str


@dataclasses.dataclass
class Track:
    artist: typing.List[Artist]  # uri (more clear for searching)
    duration: int
    explicit: bool
    name: str
    popularity: int
    release_date: datetime.datetime
    uri: str

    def __hash__(self):
        return hash(self.uri)


class PlaylistMetaData:
    """Data about the playlist that does not need to be computed by the class"""

    def __init__(self, content: typing.Dict, url=None):
        self.content = content
        self.url = url

    @property
    def owner_id(self) -> str:
        """
        Parse the response to grab the playlist's owner id.

        @return str: Spotify owner id
        """

        return self.content["owner"]["id"]

    @property
    def owner_display_name(self) -> str:
        """
        Parse the response to grab the playlist's owner name.

        @return str: Spotify owner display name
        """

        return self.content["owner"]["display_name"]

    @property
    def name(self) -> str:
        """
        Parse the response to grab the playlist name.

        @return str: Spotify playlist name
        """

        return self.content["name"]

    @property
    def id_(self) -> str:
        """
        Same as calling url_base()
        """

        return self.url_base()

    def url_base(self) -> str:
        """
        Grab the playlist id from the url.
        Raise a URLParsingException if the url is malformed
        """

        playlist_re = re.compile(
            r"https://open.spotify.com/playlist/(?P<playlist_id>.*)\?si\=.*"
        )

        if not (match := playlist_re.match(self.url)):
            # raise URLParsingException(f"[ERROR] Url {self.url} is not a valid playlist")
            raise Exception(f"[ERROR] Url {self.url} is not a valid playlist")
        return match.group("playlist_id")


class Playlist:
    """
    This class is to test the logic of the Playlist class
    without having to spam the API
    """

    def __init__(
        self,
        headers: typing.Dict,
        contents: typing.Dict,
        tracks: typing.List[Track],
        url=None,
    ):
        self.contents = contents
        self.headers = headers  # so we can make requests
        self.tracks = tracks
        self.url = url

        self.meta_data = PlaylistMetaData(self.contents, self.url)

    @classmethod
    def from_file(
        cls, headers: typing.Dict, path: typing.Union[pathlib.Path, typing.Text]
    ):
        """
        Read in a json file for debugging so you
        do not have to constantly ping the API

        @return cls : class instance that is read in from a file
        """

        with open(path, "r", encoding="utf-8") as fil_ptr:
            contents = json.loads(fil_ptr.read())
            tracks = [
                Track(
                    [Artist(uri["name"], uri["uri"]) for uri in element["artists"]],
                    element["duration_ms"],
                    element["explicit"],
                    element["name"],
                    element["popularity"],
                    datetime.datetime.strptime(
                        # element["album"]["release_date"], "%Y-%m-%d"
                        "2021-01-01",
                        "%Y-%m-%d",
                    ),
                    element["uri"],
                )
                for row in contents
                for element in row
            ]
        return cls(headers, contents, tracks)

    @classmethod
    def from_url(cls, headers: typing.Dict, url: str):
        """
        Obtain information about a given playlist from
        the API directly

        @param headers : allows for API requests to be made, contains the token
        @param url : link directly to the Spotify playlist

        @return cls : class instance of the playlist
        """

        __returnable = cls(headers, {}, [], url)

        request_url = (
            f"https://api.spotify.com/v1/playlists/{__returnable.meta_data.id_}"
        )
        request = requests.get(request_url, headers=headers)
        __returnable.contents = json.loads(request.content)

        __returnable.tracks = [
            Track(
                [Artist(uri["name"], uri["uri"]) for uri in element["artists"]],
                element["duration_ms"],
                element["explicit"],
                element["name"],
                element["popularity"],
                datetime.datetime.strptime(
                    # element["album"]["release_date"], "%Y-%m-%d"
                    "2021-01-01",
                    "%Y-%m-%d",
                ),
                element["uri"],
            )
            for row in __returnable.contents
            for element in row
        ]

        match request.status_code:
            case 200:
                pass
            case _:
                match __returnable.contents["error"]["message"]:
                    case "The access token expired":
                        raise Exception("Current token is expired, please renew")
                    case _:
                        raise Exception(f"[ERROR]: {request.text}")

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


def urlify(string: str) -> str:
    """
    Make the string usable in a URL
    Example: "iann dior" -> "iann%20dior"

    @return str : string that does not have any spaces
    """

    return string.replace(" ", "%20")


token = "BQDSQdxshIdD6RD60ep2qh4hXoR7PyFWsjSYxQBJ6lvv7VlZoWSXXOU8Qq3nF4W87E8ZDrH6ZLw0IgsHOebnEYCbTvJbClg_L-jfC_hpaZugWTq6A-VHBEDKr2F_3yry9e-UxkRF60-QsQnILgiGqHRGlndqBwqADthXm-iXO4Cg3zCk5aCCmG3zE6bU7-8P2yCHF0E3W5ctNM3Durcn5W27muu4SA"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

# playlist = Playlist.from_file(headers, pathlib.Path("__girls___log.json"))

from_url_playlist = Playlist.from_url(
    headers=headers,
    url="https://open.spotify.com/playlist/4IeI5PQYePhXaezV9HRDIr?si=48ca9e1d13434da2",
)

print(from_url_playlist.meta_data.name)

# assert(playlist +  playlist == playlist.tracks)

# assert(playlist - playlist == [])

# name = "emotions"
# artist = "iann dior"
# url = f"https://api.spotify.com/v1/search?type=track,artist&q={urlify(name)},{urlify(artist)}"
# token = "BQAGPT4QinyAvgwLdLKWnz0RecmyhA9et7gHc9UGjHWgbiHK5Xo-tTf6ZSRYJhLWSKQSh3WhW4VX-5cGBRhrZBJerr4YIeWPAOLuHpb4YU4UN6p-qQvU0let5637mVRG1fTpHNk6LYo0acAxZgUI4wULC6mTwjN9a8zRcZGtmOo2whRD6pNmN8B-hdResQovrrI6ClKIplhAbhA7ZN1j7-70Ol2qfg"

# headers = {
# "Accept": "application/json",
# "Content-Type": "application/json",
# "Authorization": f"Bearer {token}",
# }

# response = json.loads(requests.get(url, headers=headers).text)
