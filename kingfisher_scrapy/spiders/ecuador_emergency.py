import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, components


class EcuadorEmergency(SimpleSpider):
    """
    Bulk download documentation
      https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/
    Spider arguments
      sample
        Downloads a release package for the oldest year (first link in the downloads page).
    """
    name = 'ecuador_emergency'
    data_type = 'release_package'
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'COOKIES_DEBUG': True
    }

    def start_requests(self):
        yield scrapy.Request(
            'https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for row in response.xpath('//tr'):
            filename = row.xpath('td/p/strong/text()').extract_first()
            base_link = row.xpath('td/strong/a/@href').extract_first()
            if base_link:
                filename = 'ocds-' + filename + '.json'
                url = f'{base_link.replace("sharing", "fsdownload")}/{filename}'
                yield self.build_request(base_link, formatter=components(-1),
                                         meta={'next': url}, callback=self.with_cookie)

    def with_cookie(self, response):
        yield self.build_request(response.meta['next'],
                                 formatter=components(-1))
