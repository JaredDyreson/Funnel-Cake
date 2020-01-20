#!/usr/bin/env python3.8

from back_end import spotify_oauth_flow
from back_end import spot_playlist
import os
from pprint import pprint as pp
import requests
import json
import random


spotify_oauth_flow.run_application(['user-top-read'])
user_id, username, oauth_token = os.environ.get('user_id'), os.environ.get('username'), os.environ.get('oauth_token')

def categories(token: str, country=None, locale=None, limit=20, offset=0) -> list:
    if(country is None): country = US
    elif(locale is None): locale = "en_{}".format(country)
    url = "https://api.spotify.com/v1/browse/categories?country={}&locale={}_{}&limit={}&offset={}".format(country, locale, country, limit, offset)

    headers = {
      'Accept': 'application/json', 
      'Content-Type': 'application/json', 
      'Authorization': 'Bearer {}'.format(token)
    }
    response = json.loads(requests.get(url, headers=headers).content)
    return [element['name'] for element in response['categories']['items']]

print(random.choice(categories(oauth_token, "US", "en")))

