from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class HondurasONCAE(ZipSpider):
    """
    Bulk download documentation
      http://oncae.gob.hn/datosabiertos
    Spider arguments
      sample
        Download one set of releases.
    """
    name = 'honduras_oncae'
    data_type = 'release_package'

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    def start_requests(self):
        yield scrapy.Request(
            'http://oncae.gob.hn/datosabiertos',
            meta={'kf_filename': 'list.html'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        urls = response.css(".article-content ul")\
            .xpath(".//a[contains(., '[json]')]/@href")\
            .getall()
        if self.sample:
            urls = [urls[0]]
        for url in urls:
            filename = urlparse(url).path.split('/')[-1]
            yield scrapy.Request(url, meta={'kf_filename': filename})
