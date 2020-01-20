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
          client_id="e1f239ec0ee443689d6786fd3f397af1",
          client_secret="cbecd4d200f8482d910cb1db77d6f10c"
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
       else: return False


class SpotifyPlaylist(PlaylistManager):
    def __init__(self, manager: PlaylistManager, tracks: list, url=None, name=None):
      """
      Constructor for the Playlist class.
      We inherit the PlaylistManager class because we don't always want to have a manager
      object passed into our functions.
      """

      super().__init__(manager.user_id, manager.token)
      self.url = self.parse_url(url)
      self.tracks = tracks
      if(len(tracks) == 0): self.tracks = self.get_track_ids()
      self.api_response = self.get_response()
      self.name = name
      if((self.name is None) and (self.url is not None)):
        self.name = self.playlist_name()

    def __add__(self, other) -> list:
        """
        Combine both track lists into a set, casting duplicate elements out, subsequently finding the union. 
        """
        return list(set().union(self.tracks, other.tracks))

    def __sub__(self, other) -> list:
        """
        Find the intersection of both lists
        """
        return list(set(self.tracks) & set(other.tracks))
    def __eq__(self, other) -> bool:
        """
        Check if both objects are the same
        """
        return ((self.tracks == other.tracks) and (self.url == other.url))

    @classmethod
    def from_url(cls, manager: PlaylistManager, url: str):
       """
       Have all the information get gathered from API calls.
       """
       return cls(manager, [], url)

    def parse_url(self, url: str) -> str:
        """
        Choosing how we process the url given.
        It can take either be given from the iOS app or the web player.
        The iOS version is sent to the reform_url() function to be modified.
        """

        if("user" in url):
         return self.reform_url() 
        elif(url is None): return ""
        return url
        
    def url_base(self) -> str:
       """
       Grab the playlist id from the url.
       Sometimes it has a weird extension of ?si=.* which needs to be removed.
       """

       if(self.url is None): return ""

       base_split = os.path.basename(self.url).split("?si=")
       if(len(base_split) == 0):
         return os.path.basename(self.url)
       return base_split[0]

    def reform_url(self) -> str:
       """
       Conform the url to look like the web player format.
       """ 

       return "https://open.spotify.com/playlist/{}".format(self.url_base())

    def get_response(self) -> dict:
       """
       We only want to make one API request, the other functions will parse this
       response to get the necessary information.
       """

       if(self.url is None): return ""
       url = "https://api.spotify.com/v1/playlists/{}".format(self.playlist_id())
       headers = {
         'Accept': 'application/json', 
         'Content-Type': 'application/json', 
         'Authorization': 'Bearer {}'.format(self.token) 
       }
       request = requests.get(url, headers=headers)
       if(request.status_code != 200):
         raise Exception("Error: Request returned status code {}. Message: {}".format(
               request.status_code, request.text
       ))
       return json.loads(request.content)

    def playlist_owner_id(self) -> str:

        """
        Parse the response to grab the playlist's owner id.
        """

        try: return self.api_response["owner"]["id"]
        except KeyError: return ""

    def playlist_name(self) -> str:

        """
        Parse the response to grab the playlist name.
        """

        try: return self.api_response["name"]
        except KeyError: return ""

    def playlist_id(self) -> str:
       """
       Same as calling url_base()
       """

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
      """
      Remove all tracks from a playlist.
      """
      self.elevated_credentials.user_playlist_remove_all_occurrences_of_tracks(
          self.user_id, self.playlist_id(), self.tracks
      )

    def append(self, container: list) -> None:

      """
      Insert the contents of container into the current instance of the playlist.
      """
        
      track_list_uris = ["spotify:track:{}".format(element) for element in container]
      url = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks?position=0".format(self.user_id, self.playlist_id())
      headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer {}'.format(self.token)
      }
      # there is a 100 track limit per request, we need to make multiple requests if this is the case
      chunks = [track_list_uris[x:x+100] for x in range(0, len(track_list_uris), 100)]
      for uri_chunk in chunks:
        payload = {
          "position": 0, 
          "uris": uri_chunk
        }
        request = requests.post(url, headers=headers, data=json.dumps(payload))

        if(request.status_code != 201): 
          print('Error: Request returned status code {}. Returned: {}'.format(request.status_code, request.text))
      # this is the new tracks attribute
      self.tracks = container

    def get_detailed_track_info(self) -> list:
      url = "https://api.spotify.com/v1/tracks"
      headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer {}'.format(self.token)
      }

      container = ["{}/{}".format(url, track) for track in self.tracks]
      return [json.loads(requests.get(element, headers=headers).content) for element in container]
    def find_explicit(self) -> list:
        return [element['id'] for element in self.get_detailed_track_info() if(element['explicit'])]
    def find_live(self) -> list:
        container = []
        for element in self.get_detailed_track_info():
          name = element['name']
          if("live" in name.lower()): container.append(element['id'])
        return container
    def remove(self, container: list) -> None:
      url = "https://api.spotify.com/v1/playlists/{}/tracks".format(self.playlist_id())
      payload = {
        "tracks": []
      }

      headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer {}'.format(self.token)
      }

      track_list_uris = ["spotify:track:{}".format(track) for track in container]
      chunks = [track_list_uris[x:x+100] for x in range(0, len(track_list_uris), 100)]
      for row in chunks:
        for index, element in enumerate(row):
            data = {
              "uri": element,
              "position": index
            }
            payload["tracks"].append(data)
        requests.delete(url, headers=headers, data=json.dumps(payload))
        payload["tracks"] = []

