from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import BROWSER_USER_AGENT, components


class UruguayRecords(UruguayBase):
    """
    Domain
      Agencia Reguladora de Compras Estatales (ARCE)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2017-11'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    """

    name = "uruguay_records"
    custom_settings = {
        "USER_AGENT": BROWSER_USER_AGENT,
    }

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # uruguay_releases

    # SimpleSpider
    data_type = "record_package"

    # UruguayBase
    def parse_list(self, response):
        url_prefix = "https://www.comprasestatales.gub.uy/ocds/record/"

        titles = response.xpath("//item/title/text()").getall()
        if self.sample:
            titles = [titles[0]]

        for title in titles:
            # Title looks like: id_compra:1211147,release_id:llamado-1211147
            identifier = title.split(",")[0].split(":")[1]
            yield self.build_request(f"{url_prefix}{identifier}", formatter=components(-1))
