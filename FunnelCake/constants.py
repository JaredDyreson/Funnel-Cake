"""
Constants for configuration files
"""

import pathlib

CONFIG_STATE_PATH = pathlib.Path(
    "/home/jared/Projects/SpotifyAuthenticator/configuration.json"
)  # testing currently
CONFIG_STATE_PATH_ROOT = pathlib.Path(
    "/var/lib/funnelcake/configuration.json"
)  # use this in production

DUMP_LOCATION = pathlib.Path("user_dump")
