from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components, join


class EcuadorSERCOPBulk(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública (SERCOP)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2015-01'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api
    Bulk download documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos
    """
    name = 'ecuador_sercop_bulk'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2015-01'
    root_path = 'item'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = (
        'https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download'
        '?type=json&year={0:%Y}&month={0:%m}&method=all'
    )
    formatter = staticmethod(join(components(-1), extension='zip'))
