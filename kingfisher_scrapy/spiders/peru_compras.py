import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class PeruCompras(SimpleSpider):
    """
    Domain
      Peru Compras (contracts within framework agreements)
    Caveats
        The JSON data sometimes contains unescaped newline characters within strings.
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2021-08'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    """

    name = 'peru_compras'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2021-08'
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://www.catalogos.perucompras.gob.pe/ConsultaOrdenesPub/getListaDescargaMasiva?Anio=&Mes='
        yield scrapy.Request(url, method='POST', meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        for item in response.json():
            if from_date <= f"{item['C_Anio']}-{item['CodMes']}" <= until_date:
                yield self.build_request(
                    f"https://saeusceprod01.blob.core.windows.net/contproveedor/DescargaMasiva/{item['C_FileJson']}",
                    formatter=components(-1)
                )

    @handle_http_error
    def parse(self, response):
        # Replace unescaped newline characters within strings with a space.
        response = response.replace(body=response.body.replace(b'\n', b' '))
        yield from super().parse(response)
