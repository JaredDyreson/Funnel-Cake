"""
attempts to control functions that would directly manipulate Spotify playlists (more of a collection of scripts)
"""

from . import SpotifyPlaylist
from . import PlaylistManager
import re

def clone(manager: PlaylistManager, src: str, force_override=False, custom_name=None):
    if (not isinstance(manager, PlaylistManager.PlaylistManager) or
        not isinstance(src, str)):
        raise ValueError

    src = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, src)
    destination_url = manager.create(f"{src.name} | CLONED" if not custom_name else custom_name)
    if(isinstance(destination_url, bool)
       or force_override):
        if(force_override):
            print(f'[+] Truncating the contents of {src.name} and replacing contents')
            # TODO
        else:
            print(f'[ERROR] Cannot clone {src.name}, it already exists (no override specified)')
    else:
        cloned_playlist = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, destination_url)
        cloned_playlist.append(src.tracks)
        print(f"[+] Successfully cloned {src.name}")

def process_file(path: str, manager: PlaylistManager, function_pointer):
    if(not isinstance(path, str) or
       not isinstance(manager, PlaylistManager.PlaylistManager) or
       not callable(function_pointer)):
        raise ValueError

    _re = re.compile("https://open\.spotify\.com/playlist/[a-zA-Z0-9]+")

    with open(path) as f:
        for line in f.readlines():
            # README : you should always pass in a manager object to facilitate things!
            if(not _re.match(line)):
                print(f'Cannot process {line}, it does not conform to regex defined in this function')
            else:
                function_pointer(manager, line.strip())


