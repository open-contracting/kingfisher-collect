from kingfisher_scrapy.base_spiders import SimpleSpider


class PeruComprasBase(SimpleSpider):
    # BaseSpider
    date_required = True

    # SimpleSpider
    data_type = "release_package"

    # Local
    url_prefix = "https://www.catalogos.perucompras.gob.pe/ConsultaOrdenesPub/"

    def parse(self, response):
        # Replace unescaped newline characters within strings with a space.
        response = response.replace(body=response.body.replace(b"\n", b" "))
        yield from super().parse(response)
