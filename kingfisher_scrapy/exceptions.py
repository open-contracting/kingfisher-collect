class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class SpiderArgumentError(KingfisherScrapyError):
    """Raised when a spider argument's value is invalid, from a spider's from_crawler method"""


class MissingEnvVarError(KingfisherScrapyError):
    """Raised when a required environment variable is missing, from a spider's from_crawler method"""


class IncoherentConfigurationError(KingfisherScrapyError):
    """Raised when a spider is misconfigured by a developer, from a spider's __init__ method"""


class AccessTokenError(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached, from a spider callback"""


class MissingNextLinkError(KingfisherScrapyError):
    """Raised when a next link is not found on the first page of results, from a spider callback"""


class UnknownArchiveFormatError(KingfisherScrapyError):
    """Raised when the archive format of a file can't be determined from the filename, from a spider callback"""


class RetryableError(KingfisherScrapyError):
    """Raised when the response is an error, but the request can be retried"""
