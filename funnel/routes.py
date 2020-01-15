from flask import Flask, redirect, url_for, session, request, render_template, flash
from flask_oauthlib.client import OAuth, OAuthException

from funnel import application
from funnel.models import PlaylistMergeForm, PlaylistCloneForm
from spotutils import spot_playlist

from spotutils import spotify_oauth_application

import threading
import webbrowser
import os
import json
import requests
import werkzeug
##########################

"""
Important variables
"""

oauth = OAuth(application)

scope = ['playlist-modify-public', 'user-library-read', 'user-library-modify', 'user-follow-read', 'user-read-private', 'user-top-read']

SPOTIFY_APP_ID = os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_ID")
SPOTIFY_APP_SECRET = os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_SECRET")

spotify = oauth.remote_app(
  'spotify',
  consumer_key=SPOTIFY_APP_ID,
  consumer_secret=SPOTIFY_APP_SECRET,
  request_token_params={'scope': '{}'.format(*scope)},
  base_url='https://accounts.spotify.com',
  request_token_url=None,
  access_token_url='/api/token',
  authorize_url='https://accounts.spotify.com/authorize'
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

######################################################################################

"""
This is the main application of the program or the front end if you want to be fancy.
"""


@application.route("/", methods=['GET', 'POST'])

def index():
  form = PlaylistMergeForm(request.form)
  cloned_form = PlaylistCloneForm(request.form)
  u_id = os.environ.get("user_id")
  token = os.environ.get("oauth_token")
  if((u_id is None) or (token is None)):
    flash("Please authenticate yourself", 'danger')
  playlist_manager = spot_playlist.PlaylistManager(
      os.environ.get("user_id"),
      os.environ.get("oauth_token")
  )
  # if(
    # u_id := os.environ.get("user_id") is None and
    # token := os.environ.get("oauth_token") is None):
    
      # port = 5000
      # url = "http://127.0.0.1:{}".format(port)
      # threading.Timer(1.5, lambda: webbrowser.open(url)).start()
      # application.run(host="127.0.0.1", port=port, threaded=True)
      # playlist_manager.user = u_id
      # playlist_manager.token = token
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

############################################################################

"""
This is where the back end authenticator will go
"""

@application.route('/spot/')

def spot_index() -> werkzeug.wrappers.response.Response:

  """
  Base address of the site 
  """
  return redirect(url_for('login'))


@application.route('/spot/authenticate')

def login() -> werkzeug.wrappers.response.Response:
  callback = url_for(
    'spotify_authorized',
    next=request.args.get('next') or request.referrer or None,
    _external=True
  )
  return spotify.authorize(callback=callback)


@application.route('/spot/authenticate/authorized')

def spotify_authorized() -> str:
  response = spotify.authorized_response()
  if(response is None):
    return 'Access denied: reason={0} error={1}'.format(
      request.args['error_reason'],
      request.args['error_description']
    )
  if isinstance(response, OAuthException):
    return 'Access denied: {0}'.format(response.message)


  session['oauth_token'] = response['access_token']

  url = "https://api.spotify.com/v1/me"
  headers = {
    'Accept': 'application/json', 
    'Content-Type': 'application/json', 
    'Authorization': 'Bearer {}'.format(session.get('oauth_token'))
  }

  req = requests.get(url, headers=headers)
  text_response = json.loads(req.text)

  # Set environment variables so they are accessible outside the scope of this application 
  os.environ['user_id'] = text_response.get('id')
  os.environ['username'] = text_response.get('display_name')
  os.environ['oauth_token'] = response['access_token']

  # Keep the variables alive in the session if you wanted to have it all in one script
  session['user_id'] = text_response.get('id')
  session['username'] = text_response.get('display_name')

  # Kill our application
  # request.environ.get('werkzeug.server.shutdown')()
  flash("Successfully authenticated: {}".format(os.environ['username']), 'success')
  return redirect("/")

@spotify.tokengetter
def get_spotify_oauth_token() -> str:
  return session.get('oauth_token')
