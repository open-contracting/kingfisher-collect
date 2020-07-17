from scrapy.logformatter import LogFormatter


class KingfisherLogFormatter(LogFormatter):
    # https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.scraped
    def scraped(self, item, *args):
        return self._omit_data('scraped', item, *args)

    # https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.dropped
    def dropped(self, item, *args):
        return self._omit_data('dropped', item, *args)

    def _omit_data(self, method, item, *args):
        """
        Omits an item's `data` value from the log message.
        """
        item = item.copy()
        item.pop('data', None)
        return getattr(super(), method)(item, *args)
