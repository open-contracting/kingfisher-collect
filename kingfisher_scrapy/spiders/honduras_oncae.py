from io import BytesIO
from urllib.parse import urlparse
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class HondurasONCAE(BaseSpider):
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
        if response.status == 200:
            zip_file = ZipFile(BytesIO(response.body))
            for finfo in zip_file.infolist():
                data = zip_file.open(finfo.filename).read()
                yield \
                    self.save_data_to_disk(data, finfo.filename, data_type='release_package', url=response.request.url)
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
