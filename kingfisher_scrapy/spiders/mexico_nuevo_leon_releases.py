from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import MexicoNuevoLeonBase


class MexicoNuevoLeonReleases(MexicoNuevoLeonBase):
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
