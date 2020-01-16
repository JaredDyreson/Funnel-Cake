from flask import Flask

application = Flask(__name__)
application.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
application.config['consumer_key'] = "e1f239ec0ee443689d6786fd3f397af1" 
application.config['consumer_secret'] = "cbecd4d200f8482d910cb1db77d6f10c"

from funnel import routes
