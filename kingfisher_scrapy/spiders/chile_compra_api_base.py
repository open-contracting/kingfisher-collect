from abc import abstractmethod
from datetime import date

from kingfisher_scrapy.base_spiders import IndexSpider, PeriodicSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.items import FileError
from kingfisher_scrapy.util import components, handle_http_error


class ChileCompraAPIBase(IndexSpider, PeriodicSpider):
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2009-01'
    dont_truncate = True

    # PeriodicSpider
    # The path parameters are {system}/{year}/{month}/{offset}/{limit}.
    pattern = 'http://api.mercadopublico.cl/APISOCDS/OCDS/{0}/{1.year:d}/{1.month:02d}/{2}/{3}'
    formatter = staticmethod(components(-4, -1))  # year-month-offset
    start_requests_callback = 'parse_list'

    # IndexSpider
    result_count_pointer = '/pagination/total'
    limit = 100
    parse_list_callback = 'parse_page'

    # Local
    available_systems = {
        'convenio': 'listaOCDSAgnoMesConvenio',
        'licitacion': 'listaOCDSAgnoMes',
        'trato-directo': 'listaOCDSAgnoMesTratoDirecto'
    }
    system = None

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, system=system, *args, **kwargs)
        if system and spider.system not in spider.available_systems:
            raise SpiderArgumentError(f'spider argument `system`: {spider.system!r} not recognized')
        return spider

    def build_urls(self, date):
        for system in self.available_systems:
            if self.system and system != self.system:
                continue
            yield self.pattern.format(self.available_systems[system], date, 0, self.limit)

    @handle_http_error
    def parse(self, response):
        data = self.parse_list_loader(response)
        if isinstance(data, FileError):
            yield data
            return

        # Replace the "\u0000" escape sequence in the JSON string, which is rejected by PostgreSQL.
        # https://www.postgresql.org/docs/current/datatype-json.html
        response = response.replace(body=response.body.replace(b'\x00', b''))
        yield from super().parse(response)

    @handle_http_error
    def parse_page(self, response):
        data = self.parse_list_loader(response)
        if isinstance(data, FileError):
            yield data
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

    @abstractmethod
    def handle_item(self, item):
        pass

    # from IndexSpider
    def parse_list_loader(self, response):
        data = response.json()

        # Some files contain invalid packages, e.g.:
        # {
        #   "status": 500,
        #   "detail": "error"
        # }
        if 'status' in data and data['status'] != 200:
            data['http_code'] = data['status']
            return self.build_file_error_from_response(response, errors=data)

        return data

    # from IndexSpider
    def url_builder(self, value, data, response):
        # URL looks like http://api.mercadopublico.cl/APISOCDS/OCDS/listaOCDSAgnoMesTratoDirecto/2021/03/31500/100
        system = components(-5, -4)(response.request.url)
        year = int(components(-4, -3)(response.request.url))
        month = int(components(-3, -2)(response.request.url).lstrip('0'))

        return self.pattern.format(system, date(year, month, 1), value, self.limit)
