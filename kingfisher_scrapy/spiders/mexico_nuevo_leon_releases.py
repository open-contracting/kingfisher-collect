import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider


class MexicoNuevoLeonReleases(CompressedFileSpider):
    """
    Domain
      Secretaría de Movilidad y Planeación Urbana de Nuevo León
    Bulk download documentation
      https://smpu.nl.gob.mx/transparencia/acerca-del-proyecto
    """

    name = 'mexico_nuevo_leon_releases'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # mexico_nuevo_leon_records

    # SimpleSpider
    data_type = 'release_package'

    # CompressedFileSpider
    file_name_must_contain = 'ReleasePackage'

    def start_requests(self):
        url = 'https://smpu.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar'
        yield scrapy.Request(url, meta={'file_name': 'all.rar'})
