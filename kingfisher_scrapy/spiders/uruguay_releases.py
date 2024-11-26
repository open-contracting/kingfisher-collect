from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import browser_user_agent, components, handle_http_error


class UruguayReleases(UruguayBase):
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

    name = 'uruguay_releases'
    user_agent = browser_user_agent

    # SimpleSpider
    data_type = 'release_package'

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath('//item/link/text()').getall():
            yield self.build_request(url, formatter=components(-1))
