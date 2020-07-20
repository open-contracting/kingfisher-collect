import scrapy
from urllib.parse import parse_qs, urlsplit

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters, replace_parameter


class PortugalBase(SimpleSpider):
    custom_settings = {
        'DOWNLOADER_CLIENT_TLS_METHOD': 'TLSv1.0',
        'DOWNLOADER_CLIENT_TLS_CIPHERS': 'TLSv1:RSA:3DES:SHA1:DES:CBC3:SHA',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/37.0.2049.0 Safari/537.36',
    }

    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        yield scrapy.Request(self.url, headers=headers, meta={'file_name': 'offset-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        yield from self.parse(response)

        if not self.sample:
            next_url = response.request.url
            query = parse_qs(urlsplit(next_url).query)
            offset = int(query['offset'][0])
            url = replace_parameter(next_url, 'offset', offset)
            yield self.build_request(url, formatter=parameters('offset'))
