"""Module that contains the implmenation for PlaylistMetaData"""

from FunnelCake.utils import parse_url

import typing
import re
import json


class PlaylistMetaData:
    """Data about the playlist that does not need to be computed by the class"""

    def __init__(self, content: typing.Dict, url=None):
        self.content = content
        self.url = url

    @property
    def owner_id(self) -> str:
        """
        Parse the response to grab the playlist's owner id.

        @return str: Spotify owner id
        """

        return self.content["owner"]["id"]

    @property
    def description(self) -> str:
        """
        Return the description of the playlist

        @return str
        """
        return "I am a test description because this feature is broken"
        # return self.content["description"]

    @property
    def owner_display_name(self) -> str:
        """
        Parse the response to grab the playlist's owner name.

        @return str: Spotify owner display name
        """

        return self.content["owner"]["display_name"]

    @property
    def name(self) -> str:
        """
        Parse the response to grab the playlist name.

        @return str: Spotify playlist name
        """

        return self.content["name"]

    @property
    def id_(self) -> str:
        """
        Same as calling url_base()
        """

        return self.url_base()

    def url_base(self) -> str:
        """
        Grab the playlist id from the url.
        Raise a URLParsingException if the url is malformed
        """

        return parse_url(self.url)
