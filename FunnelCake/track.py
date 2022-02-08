"""
Module that contains the Track dataclass
"""

import dataclasses

@dataclasses.dataclass
class Track:
    """
    Dataclass that can represent a Spotify track
    """

    name: str
    id_: str
    liveliness: float

    def __lt__(self, rhs):
        """Sort by how live a track is"""
        return self.liveliness < rhs.liveliness
