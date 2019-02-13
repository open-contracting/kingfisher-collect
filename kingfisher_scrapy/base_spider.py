import scrapy
import requests

# This file contain base spiders all our spiders extend from, so we can add some custom functionality
#
# However, we need to do this for several base spiders. To avoid copying and pasting code between base spiders,
#  some code is put into generic functions


def _generic_get_start_time(called_on_class):
    stats = called_on_class.crawler.stats.get_stats()
    start_time = stats.get("start_time")
    return start_time


def _generic_is_sample(called_on_class):
    return hasattr(called_on_class, 'sample') and called_on_class.sample == 'true'


def _generic_spider_closed(called_on_class, spider, reason):
    if reason == 'finished' \
            and called_on_class.crawler.settings['KINGFISHER_API_URI'] \
            and called_on_class.crawler.settings['KINGFISHER_API_KEY']:

        headers = {"Authorization": "ApiKey " + called_on_class.crawler.settings['KINGFISHER_API_KEY']}
        data = {
            "collection_source": called_on_class.name,
            "collection_data_version": called_on_class._get_start_time().strftime("%Y-%m-%d %H:%M:%S"),
            "collection_sample": called_on_class.is_sample(),
        }

        response = requests.post(
            called_on_class.crawler.settings['KINGFISHER_API_URI'] + '/api/v1/submit/end_collection_store/',
            data=data,
            headers=headers)

        if not response.ok:
            spider.logger.warning(
                "Failed to post End Collection Store. API status code: {}".format(response.status_code))

# Now we have our own base spiders (that use our generic functions)


class BaseSpider(scrapy.Spider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def _get_start_time(self):
        return _generic_get_start_time(called_on_class=self)

    def is_sample(self):
        return _generic_is_sample(called_on_class=self)

    def spider_closed(self, spider, reason):
        return _generic_spider_closed(self, spider, reason)


class BaseXMLFeedSpider(scrapy.spiders.XMLFeedSpider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseXMLFeedSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def _get_start_time(self):
        return _generic_get_start_time(called_on_class=self)

    def is_sample(self):
        return _generic_is_sample(called_on_class=self)

    def spider_closed(self, spider, reason):
        return _generic_spider_closed(self, spider, reason)
