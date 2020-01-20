#!/usr/bin/env python3.8

"""
driver code during the development of this project
"""

from funnel import application
from spotutils import spot_playlist, get_personal_statistics
import os
from pprint import pprint as pp
import webbrowser
import threading
from flask import request
import time
import requests
import json

def merge(manager: spot_playlist.PlaylistManager, src_one: spot_playlist.SpotifyPlaylist, src_two: spot_playlist.SpotifyPlaylist, dst: str):
   combined_tracks = src_one + src_two 
   destination_url = manager.create(dst)
   merged_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
   merged_playlist.append(combined_tracks)

def clone(manager: spot_playlist.PlaylistManager, src: spot_playlist.SpotifyPlaylist):
    name = src.name
    destination_url = manager.create("{} - CLONED".format(name))
    cloned_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)

def get_liked_songs(manager: spot_playlist.PlaylistManager) -> list:
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {
      'Accept': 'application/json', 
      'Content-Type': 'application/json', 
      'Authorization': 'Bearer {}'.format(manager.token)
    }
    response = json.loads(requests.get(url, headers=headers).content)
    return [element['track']['id'] for element in response['items']]

def add_these(this: list, other: list):
    return (set(this) - set(other))
if(os.environ.get("user_id") is None):
  os.environ["SHUTDOWN_AFTER_AUTH"] = "YES"
  url = "http://127.0.0.1:5000/spot"
  threading.Timer(1.5, lambda: webbrowser.open(url)).start()
  application.run(threaded=True)


user_id, username, oauth_token = os.environ.get('user_id'), os.environ.get('username'), os.environ.get('oauth_token')

# get_personal_statistics.get_top_artists(oauth_token)
url = "https://open.spotify.com/playlist/3V40onZcAShMNJrfBeEmwX"
# other_url = "https://open.spotify.com/playlist/6ropIwtV9pcTon1ukSKMCZ"
manager = spot_playlist.PlaylistManager(user_id, oauth_token)
playlist = spot_playlist.SpotifyPlaylist.from_url(manager, url)

playlist.remove(playlist.find_explicit())


# playlist_copy = playlist
# other_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, other_url)

# clone(manager, playlist)

# print(len(add_these(playlist.tracks, get_liked_songs(manager))))
