from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import components, handle_http_error


class UruguayReleases(UruguayBase):
    """
    API documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    """
    name = 'uruguay_releases'
    data_type = 'release_package'

    @handle_http_error
    def parse_list(self, response):
        urls = response.xpath('//item/link/text()').getall()

        for url in urls:
            yield self.build_request(url, formatter=components(-1))
