import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class PeruComprasReleases(SimpleSpider):
    """
    Domain
      Peru Compras - Framework Agreements
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2017-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    """

    name = 'peru_compras_releases'

    # BaseSpider
    date_required = True
    default_from_date = '2017-01-01'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://www.catalogos.perucompras.gob.pe/ConsultaOrdenesPub/obtenerFiltros'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        frameworks = response.text.split("¯")[0].split("¬")
        for f in frameworks:
            framework_id = f.split("^")[0].split('-')[0]
            if framework_id:
                yield self.build_request(
                    f'https://www.catalogos.perucompras.gob.pe/ConsultaOrdenesPub/DescargaJsonOCDS'
                    f'?pAcuerdo={framework_id}&pFechaIni={from_date}&pFechaFin={until_date}',
                    formatter=parameters('pAcuerdo')
                )
