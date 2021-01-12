#!/usr/bin/env python3.8

from datetime import datetime
import argparse
import os
import threading
import re
from aenum import Enum

from SpotifyAuthenticator import application, CredentialIngestor
from SpotifyToolbox import HelperFunctions, PersonalStatistics
from FunnelCake import SpotifyHelper, PlaylistManager, SpotifyPlaylist

"""
TODO
"""

class Confidence:
    # default levels
    # margins increase/decrease at rate of 0.1 in the range [0 - 1]
    LIVE = 0.8
    ACOUSTIC = 0.23

parser = argparse.ArgumentParser()

parser.add_argument("-a", "--authenticate", help="authenticate user", action="store_false")

parser.add_argument("--analyze-playlist", help="dump useful data about a playlist (artist, genre distribution)", action="store_true")

# example usage : funnel --batch-clone --from-file "example-links.txt" --output "collated from work"

parser.add_argument("--batch-clone", help="apply functions to swathes of Spotify links", action="store_true")

parser.add_argument("--count", help="set length of action", type=int)

parser.add_argument("--clone", help="clone url given", type=str)

parser.add_argument("--currently-playing", help="get currently playing song", action="store_true")

# example usage: funnel --delimiter "|" --batch-clone --from-list "https://google.com|https://reddit.com"

parser.add_argument("--delimiter", help="delimiter for separated lists", type=str)

parser.add_argument("--dry-run", help="do not modify playlist(s) during code execution", action="store_true")

parser.add_argument("-f", "--from-file", help="read Spotify playlist links from file", type=str)

parser.add_argument("--force-override", help="force actions to happen", action="store_true")

parser.add_argument("--from-list", help="read Spotify playlist links from delimited set of strings", type=str)

parser.add_argument("--merge", help="merge two or more playlists into one", action="store_true")

parser.add_argument("-o", "--output", help="give output a destination name", type=str)

parser.add_argument("--personal-stats", help="dump user statistics like Spotify does", action="store_true")

parser.add_argument("--remove-non-explicit", help="remove all not explicit tracks", action="store_true")

parser.add_argument("--remove-explicit", help="remove all explicit tracks", action="store_true")

parser.add_argument("--remove-live", help="remove all live tracks", action="store_true")

parser.add_argument("--radom-playlist", help="generate a random playlist")

parser.add_argument("-v", "--verbosity", action="count", default=0)

parser.add_argument("--volume", help="flag that a collection of urls are apart of a volume", action="store_true")

arguments = parser.parse_args()

creds = None
path = "credentials.json"
container = []
_re = re.compile("https://open\.spotify\.com/playlist/[a-zA-Z0-9]+")

"""
ensure that the user is authenticated
"""
if(os.path.exists(path)):
    print("[+] Checking if the credentials are valid...")
    creds = CredentialIngestor.CredentialIngestor(path)
    if(not creds.is_expired(datetime.now())):
        print("[-] No need to authenticate")
    else:
        HelperFunctions.authenticate(application.run)
else:
    HelperFunctions.authenticate(application.run)

if(not creds
   or not arguments.authenticate):
    quit()

"""
create manager
"""

manager = PlaylistManager.PlaylistManager(creds.get_user_id(), creds.get_credential_hash())

"""
various functions that can be used
"""

if(arguments.dry_run):
    # TODO : implement
    print("[WARNING] Dry run activated, all actions here will not be permanent")

if(arguments.dry_run and arguments.force_override):
    print("[ERROR] Conflicting arguments --dry-run and --force-removal, cowardly refusing")
    quit()

# TODO
if(arguments.personal_stats):
    PersonalStatistics.personal_statistics()
if(arguments.from_list):
    if(not arguments.delimiter):
        print("[WARNING] Please use a delimiter such as \'|\' or ',' for string lists, defaulting to ',' (comma)")
        arguments.delimiter = ","
    container = arguments.from_list.split(arguments.delimiter)

if(arguments.from_file):
    if not(os.path.exists(arguments.from_file)):
        print(f'[ERROR] File specified at {arguments.from_file} does not exist, cowardly refusing')
    else:
        with open(arguments.from_file) as f:
            container = [x.strip() for x in f.readlines()]

if(arguments.clone):
    container.append(arguments.clone)

"""
since we've made string list and file contents indistinguishable from each other, we can apply
the same functions on them
"""

# CLONE

if(container and (arguments.clone or arguments.batch_clone)):
    for entity in container:
        if not(_re.match(entity)):
            print(f'[ERROR] URL {entity} does not conform to regex {_re}, will not process')
        else:
            print(f'[+] Cloning {entity}')
            if not(arguments.dry_run):
                SpotifyHelper.clone(manager, entity, arguments.force_override, arguments.output)
# MERGE


if(container and (arguments.merge)):
    SpotifyHelper.merge(container, manager, arguments.output)
