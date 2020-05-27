class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class AuthenticationFailureException(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached"""


class SpiderArgumentError(KingfisherScrapyError):
    """Raises when a spider argument's value is invalid"""
