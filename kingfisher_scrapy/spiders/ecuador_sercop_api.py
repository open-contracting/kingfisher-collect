from kingfisher_scrapy.base_spiders import PeriodicSpider, IndexSpider
from kingfisher_scrapy.util import components, parameters


class EcuadorSERCOPAPI(PeriodicSpider, IndexSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública (SERCOP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2015'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current month.
    API documentation
        https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api
    Bulk download documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos
    """
    name = 'ecuador_sercop_api'

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

    def parse_page(self, response):
        for data in response.json()['data']:
            yield self.build_request(f'{self.url_prefix}record?ocid={data["ocid"]}',
                                     formatter=parameters('ocid'))
