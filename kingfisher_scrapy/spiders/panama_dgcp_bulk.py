from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import parameters


class PanamaDGCPBulk(PeriodicSpider):
    """
    Domain
      Panama Dirección General de Contrataciones Públicas (DGCP)
    Caveats
      The default date for historical data is 1900-01-01
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '1900-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://ocds.panamacompraencifras.gob.pa/swagger/index.html
    """

    name = 'panama_dgcp_bulk'

    # BaseSpider
    date_format = 'date'
    date_required = True
    default_from_date = '1900-01-01'

    # SimpleSpider
    data_type = 'record_package'

    # PeriodicSpider
    formatter = staticmethod(parameters('DateFrom', 'DateTo'))
    pattern = (
      'https://ocds.panamacompraencifras.gob.pa/Descarga?DateFrom={0:%Y-%m-%d}&DateTo={1:%Y-%m-%d}&FileType=json'
    )
    # The API returns HTTP 400 error for intervals longer than a month and times out for intervals of a month.
    step = 15
