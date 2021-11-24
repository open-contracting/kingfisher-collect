import logging
import traceback

logger = logging.getLogger(__name__)


class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class MissingEnvVarError(KingfisherScrapyError):
    """Raised when a required environment variable is missing"""


class AccessTokenError(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached"""


class MissingNextLinkError(KingfisherScrapyError):
    """Raised when a next link is not found on the first page of results"""


class UnknownArchiveFormatError(KingfisherScrapyError):
    """Raised when the archive format of a file can't be determined from the filename"""


class SpiderInitializationError(KingfisherScrapyError):
    """Base class for exceptions that occur before a spider is initialized"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.error('%s\n%s', str(self), traceback.format_stack()[-2].rstrip())


class SpiderArgumentError(SpiderInitializationError):
    """Raised when a spider argument's value is invalid, from its from_crawler class method"""


class IncoherentConfigurationError(SpiderInitializationError):
    """Raised when a spider is misconfigured by a developer, from its __init__ method"""
