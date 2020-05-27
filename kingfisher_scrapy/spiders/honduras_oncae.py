from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class HondurasONCAE(ZipSpider):
    name = 'honduras_oncae'
    start_urls = ['http://oncae.gob.hn/datosabiertos']

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    @handle_error
    def parse(self, response):
        urls = response.css(".article-content ul")\
            .xpath(".//a[contains(., '[json]')]/@href")\
            .getall()
        if self.sample:
            urls = [urls[0]]
        for url in urls:
            filename = urlparse(url).path.split('/')[-1]
            yield scrapy.Request(url, meta={'kf_filename': filename}, callback=self.parse_items)

    @handle_error
    def parse_items(self, response):
        yield from self.parse_zipfile(response, data_type='release_package')
