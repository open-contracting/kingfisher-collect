import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class PeruCompras(SimpleSpider):
    """
    Domain
      Peru Compras (contracts within framework agreements)
    Caveats
        The JSON data sometimes contains unescaped newline characters within strings.
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2017-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    """

    name = 'peru_compras'

    # BaseSpider
    date_required = True
    default_from_date = '2017-01-01'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    url_prefix = 'https://www.catalogos.perucompras.gob.pe/ConsultaOrdenesPub/'

    def start_requests(self):
        url = f'{self.url_prefix}obtenerFiltros'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        # The response is a large text that looks like list_1¯list_2¯list_3
        str_lists = response.text.split('¯')
        # where the first list is the framework agreements list that we need for querying the API
        # and the items in that list are separated by ¬
        for framework in str_lists[0].split('¬'):
            # Each item has the format id-type^description and we need the id for querying the API
            # e.g.: 130-BIENES^IM-CE-2020-9 MATERIAL MÉDICO ¬128-BIENES^IM-CE-2020-8 DISPOSITIVO MÉDICO IN VITRO ¬
            framework_id = framework.split('-')[0]
            if framework_id:
                yield self.build_request(
                    f'{self.url_prefix}DescargaJsonOCDS'
                    f'?pAcuerdo={framework_id}&pFechaIni={from_date}&pFechaFin={until_date}',
                    formatter=parameters('pAcuerdo')
                )

    @handle_http_error
    def parse(self, response):
        # Replace unescaped newline characters within strings with a space.
        response = response.replace(body=response.body.replace(b'\n', b' '))
        yield from super().parse(response)
