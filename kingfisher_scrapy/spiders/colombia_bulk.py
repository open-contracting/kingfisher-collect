from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class ColombiaBulk(ZipSpider):
    """
    Bulk download documentation
      https://www.colombiacompra.gov.co/transparencia/datos-json
    Spider arguments
      sample
        Downloads the zip file and sends 10 releases to kingfisher process.
    """
    name = 'colombia_bulk'
    data_type = 'release_in_Release'
    encoding = 'iso-8859-1'
    zip_file_format = 'json_lines'

    download_warnsize = 0
    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    def start_requests(self):
        yield scrapy.Request(
            'https://www.colombiacompra.gov.co/transparencia/datos-json',
            meta={'kf_filename': 'list.html'},
            callback=self.parse_list,
        )

    @handle_error
    def parse_list(self, response):
        urls = response.css('.enlaces_contenido').css('a::attr(href)').getall()
        urls = [urls[0]] if self.sample else urls
        for url in urls:
            filename = urlparse(url).path.split('/')[-1]
            yield scrapy.Request(url, meta={'kf_filename': filename})
