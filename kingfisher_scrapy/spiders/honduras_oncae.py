from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


class HondurasONCAE(ZipSpider):
    name = 'honduras_oncae'
    start_urls = ['http://oncae.gob.hn/datosabiertos']

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    def parse(self, response):
        if response.status == 200:
            urls = response.css(".article-content ul")\
                .xpath(".//a[contains(., '[json]')]/@href")\
                .getall()
            if self.sample:
                urls = [urls[0]]
            for url in urls:
                filename = urlparse(url).path.split('/')[-1]
                yield scrapy.Request(url, meta={'kf_filename': filename}, callback=self.parse_items)
        else:
            self.logger.info(
                'Request to main site {} has failed with code {}'.format(response.url, response.status))
            raise scrapy.exceptions.CloseSpider()

    def parse_items(self, response):
        yield from self.parse_zipfile(response, data_type='release_package')
