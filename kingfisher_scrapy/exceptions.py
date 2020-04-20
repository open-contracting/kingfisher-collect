class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class AuthenticationFailureException(KingfisherScrapyError):
    """Raised when the maximum attempts to get an access token has been reached."""


class SpiderArgumentError(KingfisherScrapyError):
    """Raises when an error has occurred with the spider arguments"""
