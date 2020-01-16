#!/usr/bin/env python3.8

"""
driver code during the development of this project
"""

from funnel import application
from spotutils import spot_playlist
import os
from pprint import pprint as pp
import webbrowser
import threading
from flask import request
import time

def merge(manager: spot_playlist.PlaylistManager, src_one: spot_playlist.SpotifyPlaylist, src_two: spot_playlist.SpotifyPlaylist, dst: str):
   combined_tracks = src_one + src_two 
   destination_url = manager.create(dst)
   merged_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
   merged_playlist.append(combined_tracks)

def clone(manager: spot_playlist.PlaylistManager, src: spot_playlist.SpotifyPlaylist):
    name = src.get_name()
    destination_url = manager.create("{} - CLONED".format(name))
    cloned_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)


if(os.environ.get("user_id") is None):
  os.environ["SHUTDOWN_AFTER_AUTH"] = "YES"
  url = "http://127.0.0.1:5000/spot"
  threading.Timer(1.5, lambda: webbrowser.open(url)).start()
  application.run(threaded=True)


user_id, username, oauth_token = os.environ.get('user_id'), os.environ.get('username'), os.environ.get('oauth_token')

url = "https://open.spotify.com/playlist/5n3IEeTyqESIhwjEgkgzOA"
other_url = "https://open.spotify.com/playlist/6ropIwtV9pcTon1ukSKMCZ"
manager = spot_playlist.PlaylistManager(user_id, oauth_token)
playlist = spot_playlist.SpotifyPlaylist.from_url(manager, url)
other_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, other_url)

print(playlist.name)

