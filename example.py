#!/usr/bin/env python3.8

from FunnelCake import PlaylistManager, SpotifyPlaylist


def clone(manager: PlaylistManager, src: SpotifyPlaylist):
    name = src.name
    destination_url = manager.create(f"{name} | CLONED")
    cloned_playlist = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, destination_url)
    cloned_playlist.append(src.tracks)
    print(f"[+] Successfully cloned {name}")

DUMMY_TOKEN = "BQDKvx-LZclJHVZskW0vxOH1PbLDFq75o0Sii2G13IpaFiaNax3YWfrOzWezM7D_11GlFvvcpIcWUfUKLXuGvqS842Ez64kp5upkxt71jeO26QsqbDq2cmZWncW3KL3pFXoA-ljOCzy5l_kOWQOZfScanwJC4AJxEQTcBYE0MncYfJBo72uPBhb_S8OHFgnHnEEQtbhX_xQt--Wh1l2JRV2R"
DUMMY_ID = "12164553253"
url = "https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B"
manager = PlaylistManager.PlaylistManager(DUMMY_ID, DUMMY_TOKEN)
playlist = SpotifyPlaylist.SpotifyPlaylist.from_url(manager, url)

clone(manager, playlist)
