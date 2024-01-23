from scrapy import signals


class ItemCount:
    """
    Adds a count to the crawl stats for each type of item scraped.
    """

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls(crawler.stats)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)

        return extension

    def item_scraped(self, item, spider):
        self.stats.inc_value(f'{type(item).__name__.lower()}_count')
