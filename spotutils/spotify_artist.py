#!/usr/bin/env python3.8

"""
Wrapper class for a given artist.
Name: artist/group name
Popularity: how popular artist is with current user
Hash identifier: unique id for the artist to avoid name collisions
"""

class SpotifyArtist:
    def __init__(self, name: str, popularity: str, hash_identifier: str):
        self.name = name
        self.popularity = popularity
        self.hash_identifier = hash_identifier
