import sentry_sdk
from scrapy.exceptions import NotConfigured


# https://stackoverflow.com/questions/25262765/handle-all-exception-in-scrapy-with-sentry
class SentryLogging:
    """
    Sends exceptions and log records to Sentry. Log records with a level of ``ERROR`` or higher are captured as events.

    .. seealso::

       `Sentry documentation <https://docs.sentry.io/platforms/python/logging/>`__
    """

    def __init__(self, sentry_dsn):
        sentry_sdk.init(sentry_dsn)

    @classmethod
    def from_crawler(cls, crawler):
        sentry_dsn = crawler.settings['SENTRY_DSN']

        if not sentry_dsn:
            raise NotConfigured('SENTRY_DSN is not set.')

        extension = cls(sentry_dsn)

        return extension
