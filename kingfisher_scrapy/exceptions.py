class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class AuthenticationFailureException(KingfisherScrapyError):
    """Raised when the maximum attempts to get an access token has been reached."""
