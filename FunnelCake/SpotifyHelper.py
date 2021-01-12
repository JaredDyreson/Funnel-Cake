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
        print(f'[ERROR] Cannot clone {src.name}, it already exists (no override specified)')
        return

    cloned_playlist = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)
    print(f"[+] Successfully cloned {src.name}")

def merge(container: list, manager: PlaylistManager, output_name: str):
    if not(isinstance(container, list)
           and isinstance(manager, PlaylistManager.PlaylistManager)
           and isinstance(output_name, str)):
           raise ValueError

    print(f'[INFO] Merging {len(container)} playlists together')

    if not(output_name):
        print('[ERROR] You have not supplied an output name')
        return

    master_, names, collaborators = None, [], set()
    for element in container:
        element = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, element)
        names.append(element.name)
        collaborators.add(element.playlist_owner_display_name())
        master_ = master_ + element if master_ else element

    names, collabs = ', '.join(names), ', '.join(collaborators)

    destination_url = manager.create(output_name, True, f'Playlist from {len(container)} playlists: {names}. Collaborators(s): {collabs}')
    new_playlist = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, destination_url)

    if(isinstance(destination_url, bool)):
        print(f'[ERROR] Could not store contents of {len(container)} playlists @ "{output_name}"; already exists')
        return
    else:
        new_playlist.append(master_)
        print(f'[SUCCESS] Created {output_name} from {names}')
