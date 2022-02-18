""" Module containing the Token dataclass """

import dataclasses
import typing
import datetime
import pathlib
import json

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

from FunnelCake.constants import CONFIG_STATE_PATH


@dataclasses.dataclass
class Token:
    """
    API token obtained that will allow modification of
    playlists and user data
    """

    token_path: pathlib.Path
    header: typing.Dict = dataclasses.field(default_factory=lambda: {})

    def __post_init__(self):
        if not CONFIG_STATE_PATH.is_file():
            raise FileNotFoundError(
                f"[ERROR] Cannot find configuration file at: {CONFIG_STATE_PATH}"
            )

        if not self.token_path.is_file():
            raise FileNotFoundError(
                f"[ERROR] Cannot find token path at: {self.token_path}"
            )

        with open(CONFIG_STATE_PATH, "r", encoding="utf-8") as file_pointer:
            match json.load(file_pointer):
                case {"client_secret": client_secret, "client_id": client_id}:
                    pass
                case _:
                    raise Exception("Malformed configuration data")

        with open(self.token_path, "r", encoding="utf-8") as fil_ptr:
            match json.load(fil_ptr):
                case {
                    "user_id": _,
                    "username": _,
                    "oauth_token": token,
                    "time_expires": expiration,
                }:
                    self.token = token
                    self.expiration_date = datetime.datetime.strptime(
                        expiration, "%m/%d/%Y %H:%M:%S"
                    )
                case _:
                    raise Exception("Malformed data")

        if not client_secret or not client_id:
            raise ValueError(
                f"Please define client secret {client_secret} or"
                f"client_id {client_id} in your terminal's configuration"
            )

        self.credential_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )

        self.non_elevated_credentials = spotipy.Spotify(
            client_credentials_manager=self.credential_manager
        )

        self.elevated_credentials = spotipy.Spotify(auth=self.token)

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def expired(self) -> bool:
        """
        Check if the token is valid

        @return bool : True if expired, False otherwise
        """

        return datetime.datetime.now() > self.expiration_date
