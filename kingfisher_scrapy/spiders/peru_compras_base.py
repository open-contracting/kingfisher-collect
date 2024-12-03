from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class PeruComprasBase(SimpleSpider):
    # BaseSpider
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    # Local
    url_prefix = 'https://www.catalogos.perucompras.gob.pe/ConsultaOrdenesPub/'

    @handle_http_error
    def parse(self, response):
        # Replace unescaped newline characters within strings with a space.
        response = response.replace(body=response.body.replace(b'\n', b' '))
        yield from super().parse(response)
