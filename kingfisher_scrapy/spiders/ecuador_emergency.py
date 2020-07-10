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
        'CONCURRENT_REQUESTS': 1,
    }
    urls = []

    def start_requests(self):
        url = 'https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for row in response.xpath('//tr'):
            html_url = row.xpath('td/strong/a/@href').extract_first()
            filename = row.xpath('td/p/strong/text()').extract_first()
            if html_url:
                data_url = f'{html_url.replace("sharing", "fsdownload")}/ocds-{filename}.json'
                self.urls.append((html_url, data_url))
                if self.sample:
                    break

        yield self.request_cookie()

    def request_cookie(self):
        # This request sets a cookie, which must be used immediately to download the data. So, we set
        # `CONCURRENT_REQUESTS` to 1, and yield the requests in order.
        html_url, data_url = self.urls.pop()
        return self.build_request(html_url, meta={'next': data_url}, formatter=components(-1),
                                  callback=self.parse_page)

    @handle_http_error
    def parse_page(self, response):
        # If there is an error, a request for the data URL redirects to the html URL. To treat this as an error, we set
        # `dont_redirect`.
        yield self.build_request(response.meta['next'], meta={'dont_redirect': True}, formatter=components(-1),
                                 callback=self.parse_data)

    def parse_data(self, response):
        if self.urls:
            yield self.request_cookie()

        yield from self.parse(response)
