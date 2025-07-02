import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class ArgentinaVialidad(SimpleSpider):
    """
    Domain
      Vialidad Nacional del Ministerio de Obras Públicas
    API documentation
      https://datosabiertos.vialidad.gob.ar/ui/index.html#!/datos_abiertos
    """

    name = "argentina_vialidad"

    # BaseSpider
    root_path = "item"

    # SimpleSpider
    data_type = "release_package"

    def start_requests(self):
        url = "https://datosabiertos.vialidad.gob.ar/api/ocds/package/all"
        yield scrapy.Request(url, meta={"file_name": "all.json"})
