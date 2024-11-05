from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import MexicoNuevoLeonBase


class MexicoNuevoLeonRecords(MexicoNuevoLeonBase):
    """
    Domain
      Secretaría de Movilidad y Planeación Urbana de Nuevo León
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2013'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://smpu.nl.gob.mx/transparencia/publicaciones
    """

    name = 'mexico_nuevo_leon_records'

    # SimpleSpider
    data_type = 'record_package'
