from FunnelCake.PlaylistManager import PlaylistManager
from FunnelCake.SpotifyPlaylist import SpotifyPlaylist, clamp
from FunnelCake.SpotifyHelper import clone
import random
import requests
import json
import re
import os

class SpotifyUser(PlaylistManager):
    def __init__(self, manager: PlaylistManager, url: str):
        """
        A class to represent a Spotify user
        """

        if(not isinstance(manager, PlaylistManager)):
            raise ValueError

        self.headers = {
         'Accept': 'application/json',
         'Content-Type': 'application/json',
         'Authorization': f'Bearer {manager.token}'
        }

        self.manager = manager

        _from_user_re = re.compile("(https://open\.spotify\.com/user/(?P<ID>\w+)(\?si\=[a-zA-Z0-9]+)?)+\,?")
        match = _from_user_re.match(url)
        if(match):
            self.user_id = match.group("ID")
        else:
            raise ValueError(f'[ERROR] url {url} does not conform, not using')

        self.last_offset = 0

    def obtain_playlists(self, offset=0, limit=20) -> list:
        params = (
            ('limit', str(limit)),
            ('offset', str(offset)),
        )
        response = requests.get(f'https://api.spotify.com/v1/users/{self.user_id}/playlists', headers=self.headers, params=params)
        content = json.loads(response.text)['items']
        self.last_offset+=limit

        return [element['external_urls']['spotify'] for element in content]

    def delete_all_playlists(self):
        # TODO
        for p in self.obtain_playlists():
            SpotifyPlaylist.from_url(self.manager, p).truncate()
            requests.delete(f'https://api.spotify.com/v1/playlists/{os.path.basename(p)}/followers', headers=self.headers)

    def clone_from_dump(self, container: list, user=None) -> None:
        print(f'[INFO] Conducting mass clone from user: {user if not None else ""}')
        for url in container:
            print(f'[INFO] Processing {url}')
            # clone(self.manager, url, False, None)
            print(f'[INFO] Done processing {url}')
        print(f'[SUCESS] Mass cloning complete')
