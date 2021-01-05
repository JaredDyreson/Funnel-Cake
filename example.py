#!/usr/bin/env python3.8

import inspect

from FunnelCake import PlaylistManager, SpotifyPlaylist, SpotifyHelper

def helperfunction(inp_):
    print(inp_)

def clone(manager: PlaylistManager, src: SpotifyPlaylist):
    print(__name__)
    name = src.name
    destination_url = manager.create(f"{name} | CLONED")
    cloned_playlist = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)
    print(f"[+] Successfully cloned {name}")

def clone_driver(url: str) -> None:
    if(not isinstance(url, str)):
        raise ValueError
    """
    TODO:
    either have the user be authenticated prior or do it here?
    """

DUMMY_TOKEN = "BQAavLxyDbzBlZlnBNHIGFQZ6QLi62LgsluRrNyia6Jr-Iz4VJu-TII_NhsEHPkWeD9P2M22WVVqYRoCuSPLVxp7r-DZPgzSPtGaCGK1XORUdadZQ6V7C3v8YM4kbL-sVbQSVzK1AiSqbdVixhkU1wUJTpIbBEa5QM3m65nls-si_MMYhCPmWjdUcRZszvUXoKiQ_1iqBowJ0Mss30EGQDeS"
DUMMY_ID = "12164553253"

manager = PlaylistManager.PlaylistManager(DUMMY_ID, DUMMY_TOKEN)

SpotifyHelper.process_file("list_of_links", manager, SpotifyHelper.clone)
