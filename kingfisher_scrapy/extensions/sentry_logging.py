import sentry_sdk
from scrapy.exceptions import NotConfigured
from twisted.internet.error import ConnectionRefusedError as TxConnectionRefusedError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from twisted.internet.error import TimeoutError as TxTimeoutError
from twisted.web.client import ResponseFailed, ResponseNeverReceived

IGNORE_MESSAGES = {
    # BaseSpider.log_error_from_response
    "status=%d message=%r request=%s file_name=%s",
    # RetryDataErrorMiddleware.process_spider_exception
    "Gave up retrying %(request)s (failed %(failures)d times): %(exception)s",
}


def before_send(event, hint):
    """Filter out ERROR-level log messages about TCP, DNS and HTTP errors."""
    if "log_record" not in hint:
        return event

    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    log_record = hint["log_record"]

    # Allow CRITICAL messages.
    if log_record.levelname != "ERROR":
        return event

    if log_record.msg in IGNORE_MESSAGES or (
        # scrapy.logformatter.DOWNLOADERRORMSG_SHORT
        log_record.msg == "Error downloading %(request)s"
        and log_record.exc_info
        and issubclass(
            # https://docs.python.org/3/library/sys.html#sys.exc_info
            log_record.exc_info[0],
            # Note: ConnectError is a base class, which includes some of these plus others.
            (
                # https://docs.twisted.org/en/stable/api/twisted.internet.error.html
                DNSLookupError,
                TxConnectionRefusedError,  # errno.ECONNREFUSED
                TCPTimedOutError,  # errno.ETIMEDOUT
                TxTimeoutError,
                # https://docs.twisted.org/en/stable/api/twisted.web.client.html
                ResponseFailed,
                ResponseNeverReceived,
            ),
        )
    ):
        return None

    return event


# https://stackoverflow.com/questions/25262765/handle-all-exception-in-scrapy-with-sentry
class SentryLogging:
    """
    Sends exceptions and log records to Sentry. Log records with a level of ``ERROR`` or higher are captured as events.

    .. seealso::

       `Sentry documentation <https://docs.sentry.io/platforms/python/logging/>`__
    """

    def __init__(self, sentry_dsn):
        sentry_sdk.init(sentry_dsn, before_send=before_send)

    @classmethod
    def from_crawler(cls, crawler):
        sentry_dsn = crawler.settings["SENTRY_DSN"]

        if not sentry_dsn:
            raise NotConfigured("SENTRY_DSN is not set.")

        return cls(sentry_dsn)
