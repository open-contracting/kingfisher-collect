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
        'CONCURRENT_REQUESTS': 1
    }
    urls = []

    def start_requests(self):
        yield scrapy.Request(
            'https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/',
            meta={'file_name': 'list.html'},
            callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for row in response.xpath('//tr'):
            filename = row.xpath('td/p/strong/text()').extract_first()
            base_link = row.xpath('td/strong/a/@href').extract_first()
            if base_link:
                filename = 'ocds-' + filename + '.json'
                url = f'{base_link.replace("sharing", "fsdownload")}/{filename}'
                self.urls.append({'base': base_link, 'data': url})
        # request the same url again just for go request_cookie_save_data method
        yield self.build_request(response.request.url, callback=self.request_cookie_save_data,
                                 formatter=components(-1),
                                 dont_filter=True)

    def request_cookie_save_data(self, response):
        if self.urls:
            # we process one url and its response with its cookie at a time
            url = self.urls.pop()
            yield self.build_request(url['base'], meta={'next': url['data']},
                                     formatter=components(-1), callback=self.with_cookie)
        if 'data' in response.meta:
            yield from self.parse(response)

    def with_cookie(self, response):
        return self.build_request(response.meta['next'], formatter=components(-1),
                                  meta={'data': True,
                                        # if we send the request with the cookie and still get a redirection
                                        # it is an error so we handle it on parse
                                        'dont_redirect': True}, callback=self.request_cookie_save_data)
