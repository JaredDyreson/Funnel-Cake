"""
Helper functions that do not belong to a specific
class or series of classes
"""

from FunnelCake.funnel_cake_exceptions import URLParsingException
import re

def clamp(value: int, minn: int, maxn: int) -> int:
    """
    Given a value and a range, give a value that lies in or at the end of the range

    @param value : an integer we wish to use
    @param minn : minimum value in the range
    @param maxn : maximum value in the range

    @return int : value in the range or `maxn` if it exceeds the confines
    """

    return max(min(maxn, value), minn)

def parse_url(url: str) -> str:

    playlist_re = re.compile(
        r"https://open.spotify.com/playlist/(?P<playlist_id>.*)\?si\=.*"
    )

    if not (match := playlist_re.match(url)):
        raise URLParsingException(f"[ERROR] Url {url} is not a valid playlist")
    return match.group("playlist_id")
