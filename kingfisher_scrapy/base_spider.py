import scrapy
import requests


class BaseSpider(scrapy.Spider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def _get_start_time(self):
        stats = self.crawler.stats.get_stats()
        start_time = stats.get("start_time")
        return start_time

    def is_sample(self):
        return hasattr(self, 'sample') and self.sample == 'true'

    def spider_closed(self, spider, reason):
        if reason == 'finished' \
                and self.crawler.settings['KINGFISHER_API_URI'] \
                and self.crawler.settings['KINGFISHER_API_KEY']:

            headers = {"Authorization": "ApiKey " + self.crawler.settings['KINGFISHER_API_KEY']}
            data = {
                "collection_source": self.name,
                "collection_data_version": self._get_start_time().strftime("%Y-%m-%d %H:%M:%S"),
                "collection_sample": self.is_sample(),
            }

            response = requests.post(self.crawler.settings['KINGFISHER_API_URI'] + '/api/v1/submit/end_collection_store/',
                                     data=data,
                                     headers=headers)

            if not response.ok:
                spider.logger.warning(
                    "Failed to post End Collection Store. API status code: {}".format(response.status_code))
