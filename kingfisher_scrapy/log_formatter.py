# https://docs.scrapy.org/en/latest/topics/logging.html#custom-log-formats
import scrapy.logformatter


class LogFormatter(scrapy.logformatter.LogFormatter):
    # https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.scraped
    def scraped(self, item, *args):
        return self._omit_data('scraped', item, *args)

    # https://docs.scrapy.org/en/latest/_modules/scrapy/logformatter.html#LogFormatter.dropped
    def dropped(self, item, *args):
        return self._omit_data('dropped', item, *args)

    def _omit_data(self, method, item, *args):
        """
        Omits an item's `data` and `path` (not set yet) values from the log message.
        """
        item = item.__dict__.copy()
        if 'url' in item:
            item['url'] = str(item['url'])  # avoid pydantic.AnyUrl.__repr__
        item.pop('data', None)
        item.pop('path', None)
        return getattr(super(), method)(item, *args)
