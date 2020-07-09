import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class EcuadorEmergency(SimpleSpider):
    """
    Bulk download documentation
      https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/
    Spider arguments
      sample
        Downloads one release package from the first link in the downloads page.
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
                url = f'{base_link.replace("sharing", "fsdownload")}/ocds-{filename}.json'
                self.urls.append({'base': base_link, 'data': url})
                if self.sample:
                    break
        yield self.request_cookie()

    def request_cookie(self):
        if self.urls:
            # we process one url and its response with its cookie at a time
            url = self.urls.pop()
            return self.build_request(url['base'], meta={'next': url['data']},
                                      formatter=components(-1), callback=self.parse_page)

    def parse_page(self, response):
        return self.build_request(response.meta['next'], formatter=components(-1),
                                  meta={'data': True,
                                        # if we send the request with the cookie and still get a redirection
                                        # it is an error so we handle it on parse
                                        'dont_redirect': True}, callback=self.parse_data)

    def parse_data(self, response):
        yield self.request_cookie()
        yield from self.parse(response)
