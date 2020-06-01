from scrapy import logformatter


class KingfisherLogFormatter(logformatter.LogFormatter):
    # https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.scraped
    def scraped(self, item, response, spider):
        """
        Omits an item's `data` value from the log message.
        """
        if item:
            item = item.copy()
            item.pop('data', None)
        return super().scraped(item, response, spider)
