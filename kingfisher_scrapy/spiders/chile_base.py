from datetime import date

from kingfisher_scrapy.base_spider import IndexSpider, PeriodicSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components, handle_http_error


class ChileCompraBaseSpider(IndexSpider, PeriodicSpider):
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2009-01'

    # PeriodicSpider
    pattern = 'http://api.mercadopublico.cl/APISOCDS/OCDS/{0}/{1.year:d}/{1.month:02d}/{2}/{3}'
    start_requests_callback = 'build_periodic_requests'

    # IndexSpider
    count_pointer = '/pagination/total'
    limit = 100
    formatter = staticmethod(components(-4, -1))
    yield_list_results = False

    available_systems = {
        'convenio': 'listaOCDSAgnoMesConvenio',
        'licitacion': 'listaOCDSAgnoMes',
        'trato-directo': 'listaOCDSAgnoMesTratoDirecto'
    }
    system = None

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, system=system, *args, **kwargs)
        if system and spider.system not in spider.available_systems.keys():
            raise SpiderArgumentError(f'spider argument `system`: {spider.system!r} not recognized')
        return spider

    def build_urls(self, date):
        for system in self.available_systems.keys():
            if self.system and system != self.system:
                continue
            yield self.pattern.format(self.available_systems[system], date, 0, self.limit)

    def get_formatter(self):
        return components(-4, -1)

    @handle_http_error
    def parse(self, response):
        data = response.json()
        error = self._check_data_error(response, data)
        if error:
            yield error
            return
        yield from super().parse(response)

    @handle_http_error
    # from PeriodicSpider
    def build_periodic_requests(self, response, **kwargs):
        data = response.json()
        error = self._check_data_error(response, data)
        if error:
            yield error
            return
        yield from self.parse_page(response)
        kwargs['callback'] = self.parse_page
        yield from self.parse_list(response, **kwargs)

    def _check_data_error(self, response, data):
        # Some files contain invalid packages, e.g.:
        # {
        #   "status": 500,
        #   "detail": "error"
        # }
        if 'status' in data and data['status'] != 200:
            data['http_code'] = data['status']
            return self.build_file_error_from_response(response, errors=data)

    @handle_http_error
    def parse_page(self, response, **kwargs):
        data = response.json()
        error = self._check_data_error(response, data)
        if error:
            yield error
            return
        for item in data['data']:
            # An item looks like:
            #
            # {
            #   "ocid": "ocds-70d2nz-2359-2-LE19",
            #   "urlTender": "https://apis.mercadopublico.cl/OCDS/data/tender/2359-2-LE19",
            #   "urlAward": "https://apis.mercadopublico.cl/OCDS/data/award/2359-2-LE19",
            #   "urlPlanning": "https://apis.mercadopublico.cl/OCDS/data/planning/2359-2-LE19"
            # }
            yield from self.handle_item(item)

    # from IndexSpider
    def url_builder(self, value, data, response):
        system = components(-5, -4)(response.request.url)
        year = int(components(-4, -3)(response.request.url))
        month = int(components(-3, -2)(response.request.url).lstrip('0'))

        return self.pattern.format(system, date(year, month, 1), value, self.limit)
