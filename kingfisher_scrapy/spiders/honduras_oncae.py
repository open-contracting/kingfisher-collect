import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasONCAE(ZipSpider):
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

    @handle_http_error
    def parse_list(self, response):
        urls = response.xpath('//a[contains(., "[json]")]/@href').getall()
        if self.sample:
            urls = [urls[0]]
        for url in urls:
            # URL looks like http://200.13.162.79/datosabiertos/HC1/HC1_datos_2020_json.zip
            yield self.build_request(url, formatter=components(-1))
