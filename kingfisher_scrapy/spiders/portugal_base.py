import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    # The API return 429 error after a certain number of requests.
    download_delay = 1
    # The API returns 503 error sometimes.
    custom_settings = {
        'RETRY_TIMES': 10
    }

    # BaseSpider
    default_from_date = '2010-01-01'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = f'{url}&contractStartDate={self.from_date}&contractEndDate={self.until_date}'
        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})
