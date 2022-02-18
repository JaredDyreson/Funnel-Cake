"""
Module that contains the Track dataclass
"""
import dataclasses
import datetime
import typing


@dataclasses.dataclass
class Artist:
    """Named dictionary around artists obtained in API response"""

    name: str
    uri: str


@dataclasses.dataclass
class Track:
    """A song/element in a playlist"""

    artist: typing.List[Artist]  # uri (more clear for searching)
    duration: int
    explicit: bool
    name: str
    popularity: int
    release_date: datetime.datetime
    uri: str

    def __hash__(self):
        return hash(self.uri)
