class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class AuthenticationError(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached"""


class SpiderArgumentError(KingfisherScrapyError):
    """Raised when a spider argument's value is invalid"""


class MissingRequiredFieldError(KingfisherScrapyError, KeyError):
    """Raised when an item is missing a required field"""


class LinksSpiderError(KingfisherScrapyError):
    """Raised when a next link is invalid in LinksSpider"""
