import scrapy

from kingfisher_scrapy.spiders.peru_compras_base import PeruComprasBase
from kingfisher_scrapy.util import components, handle_http_error


class PeruComprasBulk(PeruComprasBase):
    """
    Domain
      Peru Compras (contracts within framework agreements)
    Caveats
        The JSON data sometimes contains unescaped newline characters within strings.
        The peru_compras spider contains more updated data.
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2021-08'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    """

    name = "peru_compras_bulk"

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2021-08"

    async def start(self):
        yield scrapy.Request(
            f"{self.url_prefix}getListaDescargaMasiva?Anio=&Mes=",
            method="POST",
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)

        for item in response.json():
            if from_date <= f"{item['C_Anio']}-{item['CodMes']}" <= until_date:
                yield self.build_request(
                    f"https://saeusceprod01.blob.core.windows.net/contproveedor/DescargaMasiva/{item['C_FileJson']}",
                    formatter=components(-1),
                )
