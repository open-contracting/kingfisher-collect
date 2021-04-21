from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components


class MexicoNuevoLeonReleases(CompressedFileSpider):
    """
    Domain
      Secretaría de Infraestructura del Gobierno del Estado de Nuevo León
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/acerca-del-proyecto
    """
    name = 'mexico_nuevo_leon_releases'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # mexico_nuevo_leon_records

    # SimpleSpider
    data_type = 'release_package'

    # CompressedFileSpider
    file_name_must_contain = 'ReleasePackage'

    def start_requests(self):
        yield self.build_request(
            'http://si.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar',
            formatter=components(-1)
        )
