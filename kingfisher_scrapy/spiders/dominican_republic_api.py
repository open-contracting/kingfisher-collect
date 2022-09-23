from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import parameters, components


class DominicanRepublicAPI(LinksSpider, PeriodicSpider):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2018'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
      https://api.dgcp.gob.do/api/docs
    """
    name = 'dominican_republic_api'

    # BaseSpider
    default_from_date = '2018'
    date_format = 'year'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(components(-2))

    # PeriodicSpider
    pattern = 'https://api.dgcp.gob.do/api/year/{}/1'
