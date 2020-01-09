#!/usr/bin/env python3.8

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotipy.util as util

import json
import requests
import os

class PlaylistManager(object):
    def __init__(self, user_id: str, token: str):
        self.user_id = user_id
        self.token = token
        self.credential_manager = SpotifyClientCredentials(
          client_id=os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_ID"),
          client_secret=os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_SECRET")
        )
        self.non_elevated_credentials = spotipy.Spotify(
          client_credentials_manager=self.credential_manager
        )
        self.elevated_credentials = spotipy.Spotify(
          auth=self.token
        )

    def list_user_playlists(self) -> dict:
      results = self.elevated_credentials.user_playlists(self.user_id)
      playlist_manifest = results['items']
      while results['next']:
        results = self.elevated_credentials.next(results)
        playlist_manifest.extend(results['items'])
      return playlist_manifest

    def is_playlist(self, playlist_name: str) -> bool:
        for playlist in self.list_user_playlists():
          if(playlist['name'] == playlist_name): return True
        return False


    def create(self, destination: str):
       if not(self.is_playlist(destination)):
        return self.elevated_credentials.user_playlist_create(
              self.user_id,
              destination
        )['external_urls']['spotify']
       else: return False


class SpotifyPlaylist(PlaylistManager):
    def __init__(self, manager: PlaylistManager, tracks: list, url=None, name=None):
      super().__init__(manager.user_id, manager.token)
      self.url = url
      self.tracks = tracks
      if(len(tracks) == 0): self.tracks = self.get_track_ids()
      self.name = name
      if((self.name is None) and (self.url is not None)):
        self.name = self.get_name()

    def __add__(self, other) -> list:
        return list(set().union(self.tracks, other.tracks))

    @classmethod
    def from_url(cls, manager: PlaylistManager, url: str):
       return cls(manager, [], url)

    def url_base(self) -> str:
       if(self.url is None): return ""
       return os.path.basename(self.url)

    def playlist_owner_id(self) -> str:
        if(self.url is None): return ""
        url = "https://api.spotify.com/v1/playlists/{}".format(self.playlist_id())
        headers = {
          'Accept': 'application/json', 
          'Content-Type': 'application/json', 
          'Authorization': 'Bearer {}'.format(self.token) 
        }
        request = requests.post(url, headers=headers)
        if(request.status_code != 201):
          raise Exception("Error: Request returned status code {}. Message: {}".format(
                request.status_code, request.text
          ))
        return request.content

    def playlist_id(self) -> str:
       for playlist in self.list_user_playlists():
         current_playlist_url = playlist['external_urls']['spotify']
         if(current_playlist_url == self.url): return playlist['id']
       return self.url_base()
    def get_track_ids(self) -> list:
        
      if(len(self.tracks) > 0): return []

      list_of_tracks = self.get_playlist_tracks()
      self.tracks = [list_of_tracks[index]['track']['id'] for index, element in enumerate(list_of_tracks)]
      return self.tracks

    def get_playlist_tracks(self) -> list:
      
      results = self.non_elevated_credentials.user_playlist_tracks(self.user_id, playlist_id="{}".format(self.playlist_id()))
      tracks = results['items']
      while results['next']:
        results = self.non_elevated_credentials.next(results)
        tracks.extend(results['items'])
      return tracks

    def truncate(self) -> None:
      self.elevated_credentials.user_playlist_remove_all_occurrences_of_tracks(
          self.user_id, self.playlist_id(), self.tracks
      )

    def append(self, container: list) -> None:
        
      track_list_uris = ["spotify:track:{}".format(element) for element in container]
      url = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks?position=0".format(self.user_id, self.playlist_id())
      headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer {}'.format(self.token)
      }
      chunks = [track_list_uris[x:x+100] for x in range(0, len(track_list_uris), 100)]
      for uri_chunk in chunks:
        payload = {
          "position": 0, 
          "uris": uri_chunk
        }
        request = requests.post(url, headers=headers, data=json.dumps(payload))

        if(request.status_code != 201): 
          print('Error: Request returned status code {}. Returned: {}'.format(request.status_code, request.text))
    def get_name(self) -> str:
        try:
            return self.non_elevated_credentials.user_playlist(
              user=self.playlist_owner_id(),
              playlist_id=self.playlist_id(),
              fields="name"
            )["name"]
        except IndexError: return ""
