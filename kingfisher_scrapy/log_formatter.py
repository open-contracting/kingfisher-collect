import logging

from scrapy import logformatter
from twisted.python.failure import Failure


class KingfisherCustomLoggerFormatter(logformatter.LogFormatter):
    # from https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.scraped
    def scraped(self, item, response, spider):
        """Logs a message when an item is scraped by a spider."""
        if isinstance(response, Failure):
            src = response.getErrorMessage()
        else:
            src = response
        return {
            'level': logging.DEBUG,
            # we dont log the item content just the source
            'msg': "Scraped from %(src)s",
            'args': {
                'src': src
            }
        }
