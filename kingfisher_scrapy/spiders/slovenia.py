import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class Slovenia(SimpleSpider):
    """
    Domain
      Ministry of Public Administration Slovenia
    Bulk download documentation
      http://tbfy.ijs.si/?m=tenders&a=list_data&t=si_ocds
    """
    name = 'slovenia'

    # SimpleSpider
    data_type = 'release_package'

    url = 'http://tbfy.ijs.si/public/ocds/mju/'

    def start_requests(self):
        yield scrapy.Request(self.url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        html_urls = reversed(response.xpath('//a/@href').getall())
        for number, url in enumerate(html_urls):
            if 'ocds' and 'json' in url:
                yield self.build_request(f'{self.url}{url}', formatter=components(-1), priority=number * -1)
