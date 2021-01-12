import os
import requests
import json
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib
import operator
import numpy as np
from flask import redirect
from datetime import datetime

# TODO : make sure these are installed
from SpotifyAuthenticator import CredentialIngestor
from .HelperFunctions import authenticate
# from SpotifyToolbox.SpotifyToolbox.HelperFunctions import authenticate

class SpotifyArtist():
    def __init__(self, name : str, popularity : int,
                    identifier : str):
                    if(not isinstance(name, str) or
                       not isinstance(popularity, int) or
                       not isinstance(identifier, str)):
                       raise ValueError()

                    self.identifier =  identifier
                    self.name = name
                    self.popularity = popularity
                    self.image = None

class ArtistGraph():
    def __init__(self, title : str, token : str):
        if(not isinstance(title, str) or
           not isinstance(token, str)):
            raise ValueError

        self.title = title
        self.token = token

        self.artists = self.get_top_artists()
        self.figure = self.generate_bar_graph()

    def get_top_artists(self) -> list:
          url = "https://api.spotify.com/v1/me/top/artists"
          headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
          }
          response = json.loads(requests.get(url, headers=headers).content)
          return [SpotifyArtist(
            artist['name'], int(artist['popularity']), artist['id']
            ) for artist in response['items']
          ]

    def get_artist_image_list(self, artist_id: str) -> list:
        if(not isinstance(artist_id, str)):
           raise ValueError

        url = f'https://api.spotify.com/v1/artists/{artist_id}'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        response = json.loads(requests.get(url, headers=headers).content)
        return [element['url'] for element in response['images']]

    def generate_bar_graph(self) -> matplotlib.figure.Figure:
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
        sorted_list = sorted(self.artists, key=operator.attrgetter('popularity'))
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
        axis.set_title(self.title)

        """
        Set the size of the figure:
        https://stackoverflow.com/questions/332289/how-do-you-change-the-size-of-figures-drawn-with-matplotlib
        """

        figure.set_size_inches(18.5, 10.5)
        return figure
    def save(self, filename : str, dpi_=200):
        if(not isinstance(filename, str)):
            raise ValueError
        self.figure.savefig(filename, dpi=dpi_)

def personal_statistics():
    """
    Driver code of above class implementation
    """

    path = "credentials.json"
    creds = CredentialIngestor.CredentialIngestor(path)
    if(creds.is_expired(datetime.now())):
        authenticate()
        creds = CredentialIngestor.CredentialIngestor(path)

    G = ArtistGraph(f"{creds.get_username()}\'s Favorite Artists", creds.credential_hash)
    G.save(f"{creds.get_username()} Top 20 Artists")
