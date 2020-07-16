from scrapy.logformatter import LogFormatter


class KingfisherLogFormatter(LogFormatter):
    # https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.scraped
    def scraped(self, item, response, spider):
        """
        Omits an item's `data` value from the log message.
        """
        item = item.copy()
        item.pop('data', None)
        return super().scraped(item, response, spider)
