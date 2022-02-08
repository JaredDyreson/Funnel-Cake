from FunnelCake.PlaylistManager import PlaylistManager
from FunnelCake.SpotifyPlaylist import SpotifyPlaylist, clamp

import json
import random
import requests


class PlaylistGenerator(PlaylistManager):
    def __init__(self, manager: PlaylistManager):
        """
        A class to randomly generate
        playlists based on; genres, artists, and songs
        """

        if not isinstance(manager, PlaylistManager):
            raise ValueError

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {manager.token}",
        }

        self.manager = manager

        self.genres = manager.list_genre_seeds()

        self.random_adjectives = [
            "Electric",
            "Fries",
            "Pudding",
            "Quirky",
            "Special",
            "Squirrel",
        ]
        self.random_nouns = [
            "Chowder",
            "Germs",
            "Ham",
            "Matter",
            "Patrol",
        ]
        super().__init__(manager.user_id, manager.token)

    def generate_name(self):
        return f"{random.choice(self.random_adjectives)} {random.choice(self.random_nouns)}"

    def random_genre_playlist(
        self, genre_list=None, genre_count=1, limit=10, output=None
    ) -> None:
        """
        Generate a random playlist with an arbitrary number of
        genres inside it

        @param genre_list : predefined list of valid genres
        @param genre_count : number of genres that can be used from 1 to 5
        @param limit : number of tracks inside the playlist
        @param output : name of the playlist to be created

        @return None : an API request is sent and the user should see it populate asynchronously
        """

        genre_count = clamp(genre_count, 1, 5)
        sampling = self.genres if not genre_list else genre_list

        genres = random.sample(sampling, genre_count)

        payload = (("limit", str(limit)), ("seed_genres", ",".join(genres)))

        received_content = self.send_request(payload)
        tracks = self.parse_request(received_content)

        self.generate_playlist(tracks, output, joined_genres)

    def random_artist_playlist(self, artists: list, limit=10, output=None):
        if not isinstance(artists, list):
            raise ValueError

        limit = limit if limit is not None else 10
        floor = clamp(limit, 1, 100)
        ids_ = [self.get_artist_id(artist) for artist in artists[:5]]
        joined_artists = ",".join(ids_)

        payload = (("limit", str(floor)), ("seed_artists", joined_artists))

        received_content = self.send_request(payload)
        tracks = self.parse_request(received_content)

        self.generate_playlist(tracks, output, ",".join(artists))

    def generate_playlist(self, tracks: list, output: str, dimension: str):
        if not isinstance(tracks, list):
            raise ValueError

        playlist_name = self.generate_name() if not output else output
        destination_url = self.manager.create(playlist_name)

        if isinstance(destination_url, bool):
            print(f"[ERROR] Cannot create {playlist_name}, it already exists")
            return
        src = SpotifyPlaylist.from_url(self.manager, destination_url)
        src.append(tracks)
        print(
            f"[SUCCESS] Created {playlist_name} with {len(tracks)} track(s) from these dimensions: {dimension}"
        )

    def send_request(self, parameter_contents: tuple):
        if not isinstance(parameter_contents, tuple):
            raise ValueError

        params = (
            *parameter_contents,
            ("market", "ES"),
        )

        response = requests.get(
            "https://api.spotify.com/v1/recommendations",
            headers=self.headers,
            params=params,
        )
        return json.loads(response.text)

    def parse_request(self, request: dict):
        if not isinstance(request, dict):
            raise ValueError

        return [track["id"] for track in request["tracks"]]

    def get_artist_id(self, artist: str) -> str:
        params = (
            ("q", artist),
            ("type", "artist"),
            ("limit", "1"),
        )
        response = requests.get(
            "https://api.spotify.com/v1/search", headers=self.headers, params=params
        )
        content = json.loads(response.text)
        try:
            return content["artists"]["items"][0]["id"]
        except KeyError:
            raise ValueError(f"could not find {artist} in query. please try again")
