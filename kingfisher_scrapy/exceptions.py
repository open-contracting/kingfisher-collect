class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class MissingFilename(KingfisherScrapyError):
    """Raised when an item's filename isn't set or is empty"""


class AuthenticationFailureException(KingfisherScrapyError):
    """Raised when the maximum attempts to get an access token has been reached."""
