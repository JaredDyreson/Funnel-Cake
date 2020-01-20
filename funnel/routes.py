from flask import Flask, redirect, url_for, session, request, render_template, flash, send_from_directory, current_app, make_response
from flask_oauthlib.client import OAuth, OAuthException

from funnel import application
from funnel.models import PlaylistMergeForm, PlaylistCloneForm
from spotutils import spot_playlist, get_personal_statistics

import threading
import webbrowser
import os
import json
import requests
import werkzeug
from pprint import pprint as pp

##########################

"""
Important variables
"""

oauth = OAuth(application)

scope = ['playlist-modify-public', 'user-library-read', 'user-library-modify', 'user-follow-read', 'user-read-private', 'user-top-read']

SPOTIFY_APP_ID = "e1f239ec0ee443689d6786fd3f397af1"
SPOTIFY_APP_SECRET = "cbecd4d200f8482d910cb1db77d6f10c"

spotify = oauth.remote_app(
  'spotify',
  consumer_key=SPOTIFY_APP_ID,
  consumer_secret=SPOTIFY_APP_SECRET,
  request_token_params={'scope': '{}'.format(' '.join(scope))},
  base_url='https://accounts.spotify.com',
  request_token_url=None,
  access_token_url='/api/token',
  authorize_url='https://accounts.spotify.com/authorize'
)
def merge(manager: spot_playlist.PlaylistManager, src_one: spot_playlist.SpotifyPlaylist, 
            src_two: spot_playlist.SpotifyPlaylist, dst: str, options: list):
   combined_tracks = src_one + src_two 
   destination_url = manager.create(dst)
   merged_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
   merged_playlist.append(combined_tracks)
   removed_tracks = []
   if(options):
     for option in options:
       if(option == "remove_explicit"):
          removed_tracks+=merged_playlist.find_explicit()
       elif(option == "remove_live"):
          removed_tracks+=merged_playlist.find_live()
     merged_playlist.remove(removed_tracks)
def clone(manager: spot_playlist.PlaylistManager, src: spot_playlist.SpotifyPlaylist, options: list):
    name = src.name
    destination_url = manager.create("{} - CLONED".format(name))
    cloned_playlist = spot_playlist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)
    removed_tracks = []
    if(options):
      for option in options:
        if(option == "remove_explicit"):
           removed_tracks+=cloned_playlist.find_explicit()
        elif(option == "remove_live"):
           removed_tracks+=cloned_playlist.find_live()
      cloned_playlist.remove(removed_tracks)

######################################################################################

"""
This is the front end component
"""


@application.route("/", methods=['GET', 'POST'])

def index():
  if(os.environ.get("DOWNLOAD_AFTER_REDIRECT") == "YES"):
    print("this is not working at the moment but what the hell yah know")
    os.environ["DOWNLOAD_AFTER_REDIRECT"] = "NO"
    # filename="{}_Top_Artists.png".format(os.environ.get("username"))
    # return download(filename)
    # uploads = os.path.join(current_app.root_path, application.config['UPLOAD_FOLDER'])
    # return send_from_directory(directory=uploads, filename=filename)
  
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
  if(form.validate_on_submit()):
    url_one = form.playlist_one.data
    url_two = form.playlist_two.data
    destination_name = form.playlist_output_name.data
    playlist = spot_playlist.SpotifyPlaylist.from_url(playlist_manager, url_one)
    other_playlist = spot_playlist.SpotifyPlaylist.from_url(playlist_manager, url_two)

    merge(playlist_manager, playlist, other_playlist, destination_name, options)
    try:
      flash("Merged: {} + {}".format(playlist.name, other_playlist.name), 'success')
    except Exception:
      flash("Unsucessfully merged the two playlists provided", 'danger')
    return redirect(url_for('index'))
  elif(cloned_form.validate_on_submit()):
    # clone
    options = [' '.join(request.form.getlist('explicit')), ' '.join(request.form.getlist('livetracks'))]
    url_one = cloned_form.playlist_original.data
    playlist = spot_playlist.SpotifyPlaylist.from_url(playlist_manager, url_one)
    try:
      clone(playlist_manager, playlist, options)
      flash("Cloned: {}".format(playlist.name), 'success')
    except Exception as err:
      print(err)
      flash("Unsuccessfully cloned playlist provided", 'danger')
    return redirect(url_for('index'))
  return render_template('home.html', form=form, cloned_form=cloned_form)


@application.route("/about")
def about():
  return render_template('about.html', title='About')

@application.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, application.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)

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
  if(os.environ.get("SHUTDOWN_AFTER_AUTH") == "YES"):
    request.environ.get('werkzeug.server.shutdown')()
    return redirect("https://google.com")
  session.pop('_flashes', None)
  flash("Successfully authenticated: {}".format(os.environ['username']), 'success')
  return redirect("/")

@spotify.tokengetter

def get_spotify_oauth_token() -> str:
  return session.get('oauth_token')


####################################################################################

@application.route('/stats')

def run_stats_on_user():
    u_id = os.environ.get("user_id")
    token = os.environ.get("oauth_token")
    if((u_id is None) or (token is None)):
      flash("Please authenticate yourself", 'danger')
      return redirect("/")
    top_artists = get_personal_statistics.get_top_artists(
        os.environ.get("oauth_token")
    )
    username = os.environ.get("username").replace(" ", "_")
    graph = get_personal_statistics.generate_bar_graph(top_artists, "{}'s Top Artists".format(username))
    uploads = os.path.join(current_app.root_path, application.config['UPLOAD_FOLDER'])
    filename = "{}/{}_Top_Artists.png".format(uploads, username)
    graph.savefig(filename, dpi=200)
    os.environ["DOWNLOAD_AFTER_REDIRECT"] = "YES"
    return redirect("/")
