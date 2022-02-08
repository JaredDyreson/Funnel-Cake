"""
All exceptions for the
Funnel Cake project
"""

class MessageException(Exception):
    """ Base types for exceptions that include a string message """

    def __init__(self, message):
        if not isinstance(message, str):
            raise ValueError(f'Expecting a str, obtained a {type(message)}')

        Exception.__init__(self, message)
        self.message = message

class ConfigurationNotFound(MessageException):
    """Raise when the configuration file is not found"""

class URLParsingException(MessageException):
    """Raise when a Spotify URL is malformed"""

class TokenExpiredException(MessageException):
    """Raise when the token has expired"""
