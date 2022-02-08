from FunnelCake.PlaylistManager import PlaylistManager
from FunnelCake.SpotifyPlaylist import SpotifyPlaylist, clamp
from FunnelCake.SpotifyHelper import clone

from FunnelCake.funnel_cake_exceptions import URLParsingException

import random
import requests
import json
import re
import os
import typing


class SpotifyUser:
    """
    A class to represent a Spotify user
    """

    def __init__(self, manager: PlaylistManager, url: str):
        if not isinstance(manager, PlaylistManager) and isinstance(url, str):
            raise ValueError

        self.manager = manager

        from_user_re = re.compile(r"https://open.spotify.com/user/(?P<user>.*)\?si=.*")

        if not (match := from_user_re.match(url)):
            raise URLParsingException(f"[ERROR] Url {url} does not conform")

        self.user_id = match.group("user")

        self.last_offset = 0

    def obtain_playlists(self, offset=0, limit=20) -> typing.List[str]:
        """
        Get all the playlist of the current user

        @param offset : the index of the first item to return. Default is 0
        @param limit : the maximum number of items to return. Default is 20, maximum is 50

        @return typing.List[str] : list of playlist urls
        """

        limit = clamp(limit, 0, 50)
        params = (
            ("limit", str(limit)),
            ("offset", str(offset)),
        )

        response = requests.get(
            f"https://api.spotify.com/v1/users/{self.user_id}/playlists",
            headers=self.manager.headers,
            params=params,
        )

        content = json.loads(response.text)["items"]
        self.last_offset += limit

        return [element["external_urls"]["spotify"] for element in content]

    def delete_all_playlists(self) -> None:
        """
        Remove all playlists from a user's account

        @return None : an API request is made and should be seen by the user
        """

        for playlist in self.obtain_playlists():
            instance = SpotifyPlaylist.from_url(self.manager, playlist)

            instance.truncate()
            requests.delete(
                f"https://api.spotify.com/v1/playlists/{instance.name}/followers",
                headers=self.manager.headers,
            )

    def clone_from_dump(self, container: typing.List[str]) -> None:
        """
        Clone an entire list of Spotify URLs
        This would typically be used in conjunction with migrating accounts

        @return None : `n` number of API requests are made and the user should see this populate
        """

        for url in container:
            print(f"[INFO] Processing {url}")
            # clone(self.manager, url, False, None)
            print(f"[INFO] Done processing {url}")

        print("[SUCCESS] Cloning complete")
