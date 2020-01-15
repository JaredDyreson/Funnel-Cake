#!/usr/bin/env python3.8

import requests
import json
import os
import spotify_oauth_flow
from spotify_artist import SpotifyArtist
import pickle

class Wrapper():
    def __init__(self, token: str):
        self.token = token
        self.response = None

    def generate_response(self, url: str, url_parameters: list):
        """
        Generate a response given a url, token and arguments to be fed into the url.
        """
        argc = len(url_parameters)
        if(argc != 0): url = url.format(*url_parameters)
        headers = {
          'Accept': 'application/json', 
          'Content-Type': 'application/json', 
          'Authorization': 'Bearer {}'.format(self.token)
        }
        self.response = json.loads(requests.get(url, headers=headers).content)

    def get_top_artists(self) -> list:
          url = "https://api.spotify.com/v1/me/top/artists"
          self.generate_response(url, [])
          return [SpotifyArtist(
            artist['name'], artist['popularity'], artist['id'] 
            ) for artist in self.response['items']
          ]

    def get_artist_image_list(self) -> list:
        url = "https://api.spotify.com/v1/me/top/artists"
        self.generate_response(url, [])
        return [element['url'] for element in self.response['items']['images']]
    def save_token(self, path: str) -> None:
        with open(path, 'w') as file_descriptor:
          file_descriptor.write(self.token)

def load_token(path: str) -> str:
    with open(path, 'r') as file_descriptor:
      return file_descriptor.read()

# spotify_oauth_flow.run_application(['user-top-read'])
# token = os.environ.get('oauth_token')
wrapper = Wrapper(token=load_token("token_saved.txt"))
print(wrapper.get_top_artists())
