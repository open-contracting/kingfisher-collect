class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class SpiderArgumentError(KingfisherScrapyError):
    """Raised when a spider argument's value is invalid"""


class MissingEnvVarError(KingfisherScrapyError):
    """Raised when a required environment variable is missing"""


class AccessTokenError(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached"""


class MissingNextLinkError(KingfisherScrapyError):
    """Raised when a next link is not found on the first page of results"""


class UnknownArchiveFormatError(KingfisherScrapyError):
    """Raised if the archive format of a file can't be determined from the filename"""
