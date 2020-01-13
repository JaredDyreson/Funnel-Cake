#!/usr/bin/env python3.8

"""
Revamped Flask application for AWS

External links:

Run Flask application inside a class:
https://stackoverflow.com/questions/40460846/using-flask-inside-class
https://coderwall.com/p/jo39na/python-decorators-using-self

If Python autocomplete breaks and you're testing Flask application on port 5000, here is how to find and kill the rouge process:

https://stackoverflow.com/questions/11583562/how-to-kill-a-process-running-on-particular-port-in-linux
"""

from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_oauthlib.client import OAuth, OAuthException
from front_end.forms import RegistrationForm, LoginForm, PlaylistMergeForm, PlaylistCloneForm
from flask_wtf import FlaskForm
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from werkzeug.testapp import test_app

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

import json
import requests

# from back_end import spotify_oauth_flow
from back_end import spot_playlist
import get_personal_statistics
import os
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ.get("SPOTIFY_SECRET_KEY")

playlist_manager = spot_playlist.PlaylistManager(
    os.environ.get("user_id"),
    os.environ.get("oauth_token")
)

def merge(manager: spot_playlist.PlaylistManager, src_one: spot_playlist.SpotifyPlaylist, 
            src_two: spot_playlist.SpotifyPlaylist, dst: str):
   combined_tracks = src_one + src_two 
   destination_url = manager.create(dst)
   merged_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
   merged_playlist.append(combined_tracks)

def clone(manager: spot_playlist.PlaylistManager, src: spot_playlist.SpotifyPlaylist):
    name = src.get_name()
    destination_url = manager.create("{} - CLONED".format(name))
    cloned_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)

@application.route("/", methods=['GET', 'POST'])

def index():
  form = PlaylistMergeForm(request.form)
  cloned_form = PlaylistCloneForm(request.form)
  if(form.validate_on_submit()):
    url_one = form.playlist_one.data
    url_two = form.playlist_two.data
    destination_name = form.playlist_output_name.data
    playlist = spot_playlist.SpotifyPlaylist.from_url(playlist_manager, url_one)
    other_playlist = spot_playlist.SpotifyPlaylist.from_url(playlist_manager, url_two)
    merge(playlist_manager, playlist, other_playlist, destination_name)
    flash("merge", 'success')
    return render_template('home.html', form=None, cloned_form=None)
  elif(cloned_form.validate_on_submit()):
    # clone
    url_one = cloned_form.playlist_original.data
    playlist = spot_playlist.SpotifyPlaylist.from_url(playlist_manager, url_one)
    clone(playlist_manager, playlist)
    flash("clone", 'success')
    return render_template('home.html', form=None, cloned_form=None)
  return render_template('home.html', form=form, cloned_form=cloned_form)

@application.route("/about")
def about():
  return render_template('about.html', title='About')

def hello_world():
    print("Hello world from time of: {}".format(time.strftime("%A, %d. %B %Y %I:%M:%S %p")))

"""
Run code in the background every "n" minutes.
Thanks to this post -> https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask
"""

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=get_personal_statistics.driver, trigger="interval", seconds=20)
# scheduler.start()
get_personal_statistics.driver()
# run_simple("127.0.0.1", 5001, application)
"""
Run Flask application with threading support
https://stackoverflow.com/questions/10938360/how-many-concurrent-requests-does-a-single-flask-process-receive
"""
application.run(host="127.0.0.1", port=5001, threaded=True)
# atexit.register(lambda: scheduler.shutdown())
