from kingfisher_scrapy.base_spiders import IndexSpider, PeriodicSpider
from kingfisher_scrapy.util import components, parameters


class EcuadorSERCOPAPI(PeriodicSpider, IndexSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública (SERCOP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2015'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
        https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api
    Bulk download documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos
    """
    name = 'ecuador_sercop_api'
    # The API returns HTTP error 429 after a number of requests, so we have our own retry logic.
    # We also reduce the number of concurrent requests to avoid too many failures.
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'RETRY_HTTP_CODES': [],
    }

    # BaseSpider
    date_format = 'year'
    default_from_date = '2015'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    parse_list_callback = 'parse_page'
    start_requests_callback = 'parse_list'
    total_pages_pointer = '/pages'

    # Local
    url_prefix = 'https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/'

    # PeriodicSpider
    formatter = staticmethod(components(-1))
    pattern = f'{url_prefix}search_ocds'+'?year={0}'

    def parse_list(self, response):
        if self.is_http_success(response):
            yield from super().parse_list(response)
        else:
            yield self.build_retry_request_or_file_error(response)

    def parse_page(self, response):
        if self.is_http_success(response):
            for data in response.json()['data']:
                # Some ocids have a '/' character which cannot be in a file name.
                yield self.build_request(f'{self.url_prefix}record?ocid={data["ocid"]}',
                                         formatter=lambda file_name: parameters('ocid')(file_name).replace('/', ''))
        else:
            yield self.build_retry_request_or_file_error(response)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            yield self.build_retry_request_or_file_error(response)

    def build_retry_request_or_file_error(self, response):
        if response.status == 429:
            request = response.request.copy()
            wait_time = int(response.headers.get('retry-after', 1))
            request.meta['wait_time'] = wait_time
            request.dont_filter = True
            self.logger.info('Retrying %(request)s in %(wait_time)ds: HTTP %(status)d',
                             {'request': response.request, 'status': response.status,
                              'wait_time': wait_time}, extra={'spider': self})

            return request
        else:
            return self.build_file_error_from_response(response)
