from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotipy.util as util

import json
import requests
import os

class PlaylistManager(object):
    def __init__(self, user_id : str, token: str):
        if not(isinstance(token, str) or
               isinstance(user_id, str)):
               raise ValueError

        self.token = token
        self.user_id = user_id

        client_secret, client_id = os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_SECRET"), os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_ID")

        if(not client_secret or not client_id):
            raise ValueError(f'Please define client secret {client_secret} or client_id {client_id} in your terminal\'s configuration')

        self.credential_manager = SpotifyClientCredentials(
            client_id = client_id,
            client_secret = client_secret
        )

        self.non_elevated_credentials = spotipy.Spotify(
          client_credentials_manager=self.credential_manager
        )

        self.elevated_credentials = spotipy.Spotify(
          auth=self.token
        )

    def user_playlist_names(self) -> list:
        """
        Get a list of all the playlist names a user has.
        """

        return [playlist['name'] for playlist in self.list_user_playlist_information()]

    def list_user_playlist_information(self) -> dict:
        """
        Get all the information about a user's playlists
        """

        results = self.elevated_credentials.user_playlists(self.user_id)
        playlist_manifest = results['items']
        while results['next']:
            results = self.elevated_credentials.next(results)
            playlist_manifest.extend(results['items'])
        return playlist_manifest

    def is_playlist(self, playlist_name: str) -> bool:
        """
        Check for the existence of a playlist
        """
        return (playlist_name in self.user_playlist_names())

    def create(self, destination: str):
       """
       Create a playlist and return it's link if success or False if unsuccessful.
       """

       if not(self.is_playlist(destination)):
        return self.elevated_credentials.user_playlist_create(
              self.user_id,
              destination
        )['external_urls']['spotify']
       return False
