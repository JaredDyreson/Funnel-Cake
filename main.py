from FunnelCake.PlaylistManager import PlaylistManager
from FunnelCake.SpotifyPlaylist import SpotifyPlaylist
import json

P = PlaylistManager(
    "12164553253",
    "BQDbBGeoHrjV81E0o56jHO0ZSikBXvwB2A7m2iB9b4V_Ea1g2KNFyvQvCN51WVn-14ot0uZTiqaKCKUseXC9tW713J4hz9YKsx0n7qjcJgXx1YLP0I9vCdlVU1AroXjaGChs_OHlJqMnkVBpfYj6AHV9dIZOxFFvVLo7PsgRXTmy6aWh94WGadVRHpKFaqF2aHV1XMnkFBFgLE67JHF25fFJQ_b17g",
)

playlist = SpotifyPlaylist.from_url(P, "https://open.spotify.com/playlist/7xu1xG7tJLtjVy8Mlscnwy?si=165c279daa6246a1")

detailed_information = playlist.get_detailed_track_info()

# print(len(detailed_information))

with open(f"output/{playlist.name}_log.json", "w") as fp:
    fp.write(json.dumps(detailed_information))
# for i, element in enumerate(detailed_information):
