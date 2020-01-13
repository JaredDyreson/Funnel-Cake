#!/usr/bin/env python3.8

import os
import requests
from back_end import spotify_oauth_flow
import json
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib
import operator
import numpy as np
from flask import redirect

class SpotifyArtist:
    def __init__(self, name: str, popularity: str, hash_identifier: str):
        self.name = name
        self.popularity = popularity
        self.hash_identifier = hash_identifier

def get_top_artists(token: str):
      url = "https://api.spotify.com/v1/me/top/artists"
      headers = {
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer {}'.format(token)
      }
      response = json.loads(requests.get(url, headers=headers).content)
      return [SpotifyArtist(
        artist['name'], artist['popularity'], artist['id'] 
        ) for artist in response['items']
      ]

def get_artist_image_list(artist_id: str, token: str) -> list:
    url = "https://api.spotify.com/v1/artists/{}".format(artist_id)
    headers = {
      'Accept': 'application/json', 
      'Content-Type': 'application/json', 
      'Authorization': 'Bearer {}'.format(token)
    }
    response = json.loads(requests.get(url, headers=headers).content)
    return [element['url'] for element in response['images']]

def generate_bar_graph(top_artists: list, title: str) -> matplotlib.figure.Figure:
    """
    Generate an inverted bar graph of your top 20 artists on Spotify.
    This function will return the matplotlib figure object for further procecessing.

    Original code

    https://matplotlib.org/gallery/lines_bars_and_markers/barh.html

    Initial inspiration:
    https://i.ytimg.com/vi/a3w8I8boc_I/maxresdefault.jpg
    """

    plt.rcdefaults()
    figure, axis = plt.subplots()
    """
    Sort the list by a class attribute:
    https://stackoverflow.com/questions/4010322/sort-a-list-of-class-instances-python/4010558
    """
    sorted_list = sorted(top_artists, key=operator.attrgetter('popularity'))
    artists = [artist.name for artist in sorted_list]
    number_of_artists = len(artists)

    y_position = np.arange(number_of_artists)
    sheer_popularity = [artist.popularity for artist in sorted_list]
    error = np.random.rand(number_of_artists)

    axis.barh(y_position, sheer_popularity,  xerr=error, align='center')
    axis.set_yticks(y_position)
    axis.set_yticklabels(artists)
    axis.invert_yaxis()
    axis.set_xlabel("Artist Popluarity")
    axis.set_title(title)
    """
    Set the size of the figure:
    https://stackoverflow.com/questions/332289/how-do-you-change-the-size-of-figures-drawn-with-matplotlib
    """
    figure.set_size_inches(18.5, 10.5)
    return figure

def driver():
  if(os.environ.get('oauth_token') is None):
    print("running auth flow")
    spotify_oauth_flow.run_application(['user-top-read'])
  user_id, username, oauth_token = os.environ.get('user_id'), os.environ.get('username'), os.environ.get('oauth_token')

  top_artists = get_top_artists(oauth_token)

  graph = generate_bar_graph(top_artists, "Jared's Top Artists")
  print("saving the graph.....")
  graph.savefig("Jared_Top_Artists.png", dpi=200)
