from flask import Flask

from flask_oauthlib.client import OAuth

spotify_oauth_application = Flask(__name__)
spotify_oauth_application.config['SECRET_KEY'] = '5791628bb0b13ce0ce280ba245'

from funnel import routes
