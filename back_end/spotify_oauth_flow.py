#!/usr/bin/env python3.8

"""
Authenticate a user to have access to their Spotify data
"""

from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
from multiprocessing import Process
import os
import requests
import json
import werkzeug
from werkzeug.serving import run_simple
import threading
import webbrowser
import time
from selenium import webdriver

SPOTIFY_APP_ID = os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_ID")
SPOTIFY_APP_SECRET = os.environ.get("SPOTIFY_AUTHENTICATOR_CLIENT_SECRET")

app = Flask(__name__)
app.debug = False
app.secret_key = 'development'
oauth = OAuth(app)

scope = ['playlist-modify-public', 'user-library-read', 'user-library-modify', 'user-follow-read', 'user-read-private', 'user-top-read']

spotify = oauth.remote_app(
  'spotify',
  consumer_key=SPOTIFY_APP_ID,
  consumer_secret=SPOTIFY_APP_SECRET,
  request_token_params={'scope': '{}'.format(scope)},
  base_url='https://accounts.spotify.com',
  request_token_url=None,
  access_token_url='/api/token',
  authorize_url='https://accounts.spotify.com/authorize'
)

@app.route('/')

def index() -> werkzeug.wrappers.response.Response:

  """
  Base address of the site 
  """
  return redirect(url_for('login'))


@app.route('/authenticate')

def login() -> werkzeug.wrappers.response.Response:
  callback = url_for(
    'spotify_authorized',
    next=request.args.get('next') or request.referrer or None,
    _external=True
  )
  return spotify.authorize(callback=callback)


@app.route('/authenticate/authorized')

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
  request.environ.get('werkzeug.server.shutdown')()
  return redirect("/")

@spotify.tokengetter
def get_spotify_oauth_token() -> str:
  return session.get('oauth_token')

def run_application(scopes: list):
  """
  This code is a little janky because webbrowser does not support closing tabs.
  If the machine has Firefox installed, we are going to try to open a selenium driver.
  This will allow us to close the driver instance when we are done with the authentication.
  For everyone else, we will stick wit the webbrowser equivalent and will need to close it manually.

  Original code:
  https://stackoverflow.com/questions/11125196/python-flask-open-a-webpage-in-default-browser
  """
  if(len(scopes) != 0):
    spotify.request_token_params['scope'] = scopes
  port = 5000
  url = "http://127.0.0.1:{}".format(port)
  browser_name = webbrowser.get().name
  driver = None
  if(browser_name == "firefox"):
    from selenium.webdriver.firefox.options import Options
    headless_ = Options()
    headless_.headless = False
    driver = webdriver.Firefox(options=headless_)
    threading.Timer(1.25, lambda: driver.get(url)).start()
  else:
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
  app.run(port=port, debug=False)
  if(driver is not None): driver.quit()
