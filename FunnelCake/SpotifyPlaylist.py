import json
import os
import re
import requests

import typing
from FunnelCake.PlaylistManager import PlaylistManager
from FunnelCake.track import Track
from FunnelCake.funnel_cake_exceptions import URLParsingException, TokenExpiredException
from FunnelCake.utils import clamp



class SpotifyPlaylist:
    """
    Representation of a Spotify playlist
    """

    def __init__(
        self, manager: PlaylistManager, tracks: typing.List[str], url=None, name=None
    ):

        if not (
                isinstance(manager, PlaylistManager) and isinstance(tracks, typing.List)
        ):
            raise ValueError

        self.url = self.url_base() if not url else url
        self.manager = manager
        self.api_response = self.get_response()
        self.tracks = self.get_track_ids() if not tracks else tracks


        self.name = name
        if (self.name is None) and (self.url is not None):
            self.name = self.retrieved_name

    @classmethod
    def from_url(cls, manager: PlaylistManager, url: str):
        """
        Have all the information get gathered from API calls.
        """

        return cls(manager, [], url)

    def __add__(self, rhs) -> typing.List[str]:
        """
        Merge both lists into a dictionary, preserving the
        order of insertion

        @param rhs: other side of the '+' operator

        @return typing.List[str] : combined list of tracks, with no duplicates
        """

        return list(dict.fromkeys(self.tracks + rhs.tracks).keys())

    def __sub__(self, rhs) -> typing.List[str]:
        """
        Find the intersection of both lists

        @return typing.List[str] : remove all tracks that are in common between the tracks
        """

        return self.tracks & rhs.tracks

    def __eq__(self, rhs) -> bool:
        """
        Check if both objects are the same

        @return bool : True if the same, else False
        """

        return (self.tracks == rhs.tracks) and (self.url == rhs.url)


    def url_base(self) -> str:
        """
        Grab the playlist id from the url.
        Raise a URLParsingException if the url is malformed
        """

        playlist_re = re.compile(
            r"https://open.spotify.com/playlist/(?P<playlist_id>.*)\?si\=.*"
        )

        if not (match := playlist_re.match(self.url)):
            raise URLParsingException(f"[ERROR] Url {self.url} is not a valid playlist")
        return match.group("playlist_id")

    def get_response(self) -> typing.Dict:
        """
        We only want to make one API request, the other functions will parse this
        response to get the necessary information.
        """

        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}"
        request = requests.get(url, headers=self.manager.headers)
        __dict = json.loads(request.content)
        match request.status_code:
            case 200:
                pass
            case _:
                match __dict["error"]["message"]:
                    case "The access token expired":
                        raise TokenExpiredException("Current token is expired, please renew")
                    case _:
                        raise Exception(f'[ERROR]: {request.text}')
        return __dict

    @property
    def playlist_owner_id(self) -> str:
        """
        Parse the response to grab the playlist's owner id.

        @return str: Spotify owner id
        """

        return self.api_response["owner"]["id"]

    @property
    def playlist_owner_display_name(self) -> str:
        """
        Parse the response to grab the playlist's owner name.

        @return str: Spotify owner display name
        """

        return self.api_response["owner"]["display_name"]

    @property
    def retrieved_name(self) -> str:
        """
        Parse the response to grab the playlist name.

        @return str: Spotify playlist name
        """

        return self.api_response["name"]

    @property
    def playlist_id(self) -> str:
        """
        Same as calling url_base()
        """

        return self.url_base()

    def get_track_ids(self) -> typing.List[str]:
        """
        Obtain a list of track ids

        @return typing.List[str] : track ids
        """

        list_of_tracks = self.get_playlist_tracks()
        self.tracks = [
            list_of_tracks[i]["track"]["id"]
            for i in range(0, len(list_of_tracks))
        ]
        return self.tracks

    def get_playlist_tracks(self) -> typing.List:
        """
        Get all information about tracks on any given playlist
        """

        results = self.manager.non_elevated_credentials.user_playlist_tracks(
            self.playlist_owner_id, playlist_id=self.playlist_id
        )
        tracks = results["items"]
        while results["next"]:
            results = self.manager.non_elevated_credentials.next(results)
            tracks.extend(results["items"])
        return tracks

    # def append(self, container: list) -> None:

        # """
        # Insert the contents of container into the current instance of the playlist.
        # """

        # track_list_uris = [f"spotify:track:{uri}" for uri in container]
        # url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists/{self.playlist_id}/tracks?position=0"
        # # there is a 100 track limit per request, we need to make multiple requests if this is the case
        # chunks = [
            # track_list_uris[x : x + 100] for x in range(0, len(track_list_uris), 100)
        # ]
        # for uri_chunk in chunks:
            # payload = {"position": 0, "uris": uri_chunk}
            # request = requests.post(url, headers=self.headers, data=json.dumps(payload))

            # match request.status_code:
                # case 201:
                    # pass
                # case _:

                    # raise ConnectionRefusedError(
                        # f"Code: {request.status_code}"
                    # )

        # # this is the new tracks attribute
        # self.tracks = container

    def get_detailed_track_info(self) -> typing.List:
        chunks = [self.tracks[x : x + 50] for x in range(0, len(self.tracks), 50)]
        container = []
        for chunk in chunks:
            params = (
                ("ids", ",".join(chunk)),
                ("market", "ES"),
            )

            response = requests.get(
                "https://api.spotify.com/v1/tracks", headers=self.manager.headers, params=params
            )
            container.append(json.loads(response.text)["tracks"])
        return container

    # def find_explicit(self) -> list:
        # container = []
        # for element in self.get_detailed_track_info():
            # for subelement in element:
                # if subelement["explicit"]:
                    # container.append({subelement["id"]: subelement["name"]})
        # return container

    # # FIXME : Missing functions, please consult the orignial branch
    # def get_asset(self, url: str, output=None) -> None:
        # request = requests.get(url)
        # name = os.path.basename(url) if not output else output
        # with open(name, "wb") as f:
            # f.write(request.content)
        # print(f"[+] Saved asset at {name}")

    # def get_cover(self):
        # response = requests.get(
            # f"https://api.spotify.com/v1/playlists/{self.playlist_id()}/images",
            # headers=self.headers,
        # )
        # url = json.loads(response.text)[0]["url"]
        # self.get_asset(url, f"{self.name} Cover Art.png")
