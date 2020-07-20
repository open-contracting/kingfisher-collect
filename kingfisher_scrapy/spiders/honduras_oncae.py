import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasONCAE(CompressedFileSpider):
    """
    Bulk download documentation
      http://oncae.gob.hn/datosabiertos
    Spider arguments
      sample
        Downloads the first package listed on the downloads page.
    """
    name = 'honduras_oncae'
    data_type = 'release_package'
    skip_latest_release_date = 'Already covered (see code for details)'  # honduras_portal_releases

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    def start_requests(self):
        yield scrapy.Request(
            'http://oncae.gob.hn/datosabiertos',
            meta={'file_name': 'list.html'},
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
