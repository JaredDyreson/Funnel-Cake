"""
Helper functions that do not belong to a specific
class or series of classes
"""

def clamp(value: int, minn: int, maxn: int) -> int:
    """
    Given a value and a range, give a value that lies in or at the end of the range

    @param value : an integer we wish to use
    @param minn : minimum value in the range
    @param maxn : maximum value in the range

    @return int : value in the range or `maxn` if it exceeds the confines
    """

    return max(min(maxn, value), minn)
