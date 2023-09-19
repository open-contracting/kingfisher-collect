from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components


class HondurasSEFINBulk(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2012'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://www.sefin.gob.hn/edca/
    Swagger API documentation
      https://guancasco.sefin.gob.hn/EDCA_WEBAPI/swagger/ui/index
    """
    name = 'honduras_sefin_bulk'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2012'
    line_delimited = True

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'https://piep.sefin.gob.hn/edca/ocid_sefin_{}.zip'
    formatter = staticmethod(components(-1))  # filename containing year
