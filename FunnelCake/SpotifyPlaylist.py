from FunnelCake.PlaylistManager import PlaylistManager

import json
import os
import re
import requests
from collections import ChainMap
from pprint import pprint

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class Track():
    def __init__(self, name: str, id_ : str, liveliness: float):
        if not(isinstance(name, str) and
               isinstance(id_, str) and
               isinstance(liveliness, float)):
               raise ValueError
        self.name = name
        self.id_ = id_
        self.liveliness = liveliness

class SpotifyPlaylist(PlaylistManager):
    def __init__(self, manager: PlaylistManager, tracks: list, url=None, name=None):
        """
        Constructor for the Playlist class.
        We inherit the PlaylistManager class because we don't always want to have a manager
        object passed into our functions.
        """

        if(not isinstance(manager, PlaylistManager) or
           not isinstance(tracks, list)):
            raise ValueError

        self.headers = {
         'Accept': 'application/json',
         'Content-Type': 'application/json',
         'Authorization': f'Bearer {manager.token}'
        }

        self.tracks = []
        super().__init__(manager.user_id, manager.token)
        self.url = self.parse_url(url)

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

        if not(self.url): return ""

        base_split = os.path.basename(self.url).split("?si=")
        return os.path.basename(self.url) if not base_split else base_split[0]

    def reform_url(self) -> str:
       """
       Conform the url to look like the web player format.
       """

       return f"https://open.spotify.com/playlist/{self.url_base()}"

    def get_response(self) -> dict:
       """
       We only want to make one API request, the other functions will parse this
       response to get the necessary information.
       """

       if not(self.url): return ""

       url = f"https://api.spotify.com/v1/playlists/{self.playlist_id()}"
       # headers = {
         # 'Accept': 'application/json',
         # 'Content-Type': 'application/json',
         # 'Authorization': f'Bearer {self.token}'
       # }
       request = requests.get(url, headers=self.headers)
       if(request.status_code != 200):
         raise Exception(f"Error: Request returned status code {request.status_code}. Message: {request.text}")
       return json.loads(request.content)

    def playlist_owner_id(self) -> str:

        """
        Parse the response to grab the playlist's owner id.
        """

        try: return self.api_response["owner"]["id"]
        except KeyError: return ""

    def playlist_owner_display_name(self) -> str:

        """
        Parse the response to grab the playlist's owner name.
        """

        return self.api_response["owner"]["display_name"]

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
      results = self.non_elevated_credentials.user_playlist_tracks(self.user_id, playlist_id=self.playlist_id())
      tracks = results['items']
      while results['next']:
        results = self.non_elevated_credentials.next(results)
        tracks.extend(results['items'])
      return tracks

    def append(self, container: list) -> None:

        """
        Insert the contents of container into the current instance of the playlist.
        """

        track_list_uris = [f"spotify:track:{uri}" for uri in container]
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists/{self.playlist_id()}/tracks?position=0"
        # there is a 100 track limit per request, we need to make multiple requests if this is the case
        chunks = [track_list_uris[x:x+100] for x in range(0, len(track_list_uris), 100)]
        for uri_chunk in chunks:
            payload = {
                "position": 0,
                "uris": uri_chunk
            }
            request = requests.post(url, headers=self.headers, data=json.dumps(payload))

            if(request.status_code != 201):
                raise ValueError(f'Error: Request returned status code {request.status_code}. Returned: {request.text}')
        # this is the new tracks attribute
        self.tracks = container

    def get_detailed_track_info(self) -> list:
        chunks = [self.tracks[x:x+50] for x in range(0, len(self.tracks), 50)]
        container = []
        for chunk in chunks:
            params = (
                ('ids', ','.join(chunk)),
                ('market', 'ES'),
            )

            response = requests.get('https://api.spotify.com/v1/tracks', headers=self.headers, params=params)
            container.append(response.text)
        return [json.loads(response)['tracks'] for response in container]

    def find_explicit(self) -> list:
        container = []
        for element in self.get_detailed_track_info():
            for subelement in element:
                if(subelement['explicit']):
                    container.append({subelement['id']: subelement['name']})
        return container

    def find_live(self, confidence=0) -> list:
        chunks = [self.tracks[x:x+100] for x in range(0, len(self.tracks), 100)]
        container = []
        tracks = []
        for chunk in chunks:
            params = (
                ('ids', ','.join(chunk)),
            )

            response = requests.get('https://api.spotify.com/v1/audio-features', headers=self.headers, params=params)
            for element in json.loads(response.text)['audio_features']:
                if(element['liveness'] >= (clamp(0.8 + confidence, 0, 1))):
                    tracks.append(element['id'])
        return tracks

    def remove(self, container: list) -> None:
      url = "https://api.spotify.com/v1/playlists/{}/tracks".format(self.playlist_id())
      payload = {
        "tracks": []
      }

      track_list_uris = [f"spotify:track:{track}" for track in container]
      chunks = [track_list_uris[x:x+100] for x in range(0, len(track_list_uris), 100)]
      for row in chunks:
        for index, element in enumerate(row):
            data = {
              "uri": element,
              "position": index
            }
            payload["tracks"].append(data)
        requests.delete(url, headers=self.headers, data=json.dumps(payload))
        payload["tracks"] = []

    def truncate(self) -> None:
      """
      Remove all tracks from a playlist.
      """
      self.elevated_credentials.user_playlist_remove_all_occurrences_of_tracks(
          self.user_id, self.playlist_id(), self.tracks
      )

    def remove_explicits(self):
        explicits = self.find_explicit()
        for track in explicits:
            self.remove(list(track.keys()))

    def remove_non_explicits(self):
        exps = set()
        explicits = self.find_explicit()
        for track in explicits:
            exps.add(*list(track.keys()))
        explicits = exps
        non_explicits = list(set(self.tracks) - explicits)
        self.remove(non_explicits)

    def remove_live_tracks(self):
        self.remove(self.find_live())

    def get_asset(self, url: str, output=None) -> None:
        request = requests.get(url)
        name = os.path.basename(url) if not output else output
        with open(name, 'wb') as f:
            f.write(request.content)
        print(f'[+] Saved asset at {name}')

    def get_cover(self):
        response = requests.get(f'https://api.spotify.com/v1/playlists/{self.playlist_id()}/images', headers=self.headers)
        url = json.loads(response.text)[0]['url']
        self.get_asset(url, f'{self.name} Cover Art.png')
