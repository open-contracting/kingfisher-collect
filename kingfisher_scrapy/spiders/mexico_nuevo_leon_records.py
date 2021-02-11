from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import MexicoNuevoLeonBase


class MexicoNuevoLeonRecords(MexicoNuevoLeonBase):
    """
    Domain
      Secretaría de Infraestructura del Gobierno del Estado de Nuevo León
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/acerca-del-proyecto
    """
    name = 'mexico_nuevo_leon_records'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # mexico_nuevo_leon_releases

    # SimpleSpider
    data_type = 'record_package'

    # CompressedFileSpider
    file_name_must_contain = 'RecordPackage'
