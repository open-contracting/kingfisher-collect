from scrapy.utils import spider


class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class SpiderInitError(KingfisherScrapyError):
    """Base class for exceptions raised while initializing spiders"""
    def __init__(self, error):
        spider.logger.error(error)


class SpiderArgumentError(SpiderInitError):
    """Raised when a spider argument's value is invalid"""


class MissingEnvVarError(SpiderInitError):
    """Raised when a required environment variable is missing"""


class AccessTokenError(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached"""


class MissingNextLinkError(KingfisherScrapyError):
    """Raised when a next link is not found on the first page of results"""


class UnknownArchiveFormatError(KingfisherScrapyError):
    """Raised when the archive format of a file can't be determined from the filename"""


class IncoherentConfigurationError(SpiderInitError):
    """Raised when a spider is misconfigured by a developer"""
