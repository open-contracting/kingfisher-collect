from functools import partial
from urllib.parse import urlsplit

import sentry_sdk
from scrapy.exceptions import (
    CannotResolveHostError,
    DownloadConnectionRefusedError,
    DownloadFailedError,
    DownloadTimeoutError,
    NotConfigured,
)

# This subclass of ConnectError isn't wrapped by Scrapy's wrap_twisted_exceptions().
# https://docs.twisted.org/en/stable/api/twisted.internet.error.html
from twisted.internet.error import TCPTimedOutError

IGNORE_MESSAGES = {
    # BaseSpider.log_error_from_response
    "status=%d message=%r request=%s file_name=%s",
    # RetryDataErrorMiddleware.process_spider_exception
    "Gave up retrying %(request)s (failed %(failures)d times): %(exception)s",
    # scrapy.downloadermiddlewares.retry.get_retry_request
    "Gave up retrying %(request)s (failed %(retry_times)d times): %(reason)s",
}

SECRET_SETTINGS = (
    "CF_CLEARANCE",
    "KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN",
    "KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET",
    "KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN",
)


def get_secrets(settings):
    """Return the values of secret settings."""
    secrets = [settings[name] for name in SECRET_SETTINGS]
    # The last path segment is the secret. urllib3 exception messages contain the path, but not the full URL.
    if url := settings["SLACK_WEBHOOK_URL"]:
        secrets.append(url.rsplit("/", 1)[-1])
    if url := settings["RABBIT_URL"]:
        secrets.append(urlsplit(url).password)
    return [secret for secret in secrets if secret]


def scrub(value, secrets):
    """Replace secrets in all strings in an event."""
    if isinstance(value, str):
        for secret in secrets:
            value = value.replace(secret, "[Filtered]")
        return value
    if isinstance(value, dict):
        return {k: scrub(v, secrets) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [scrub(v, secrets) for v in value]
    return value


def before_send(event, hint, secrets=()):
    """Scrub secrets, and filter out ERROR-level log messages about TCP, DNS and HTTP errors."""
    event = scrub(event, secrets)

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
            (
                CannotResolveHostError,
                DownloadConnectionRefusedError,
                DownloadFailedError,
                DownloadTimeoutError,
                TCPTimedOutError,
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

    def __init__(self, sentry_dsn, secrets=()):
        sentry_sdk.init(sentry_dsn, before_send=partial(before_send, secrets=secrets))

    @classmethod
    def from_crawler(cls, crawler):
        sentry_dsn = crawler.settings["SENTRY_DSN"]

        if not sentry_dsn:
            raise NotConfigured("SENTRY_DSN is not set.")

        return cls(sentry_dsn, get_secrets(crawler.settings))
