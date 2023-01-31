from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import parameters, date_range_by_interval


class PanamaDGCPBulk(SimpleSpider):
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

    def start_requests(self):
        # The API returns error 400 for intervals longer than a month and timeout for a month.
        for start_date, end_date in date_range_by_interval(self.from_date, self.until_date, 15):
            yield self.build_request(
                f'https://ocds.panamacompraencifras.gob.pa/Descarga?DateFrom={start_date.strftime(self.date_format)}'
                f'&DateTo={end_date.strftime(self.date_format)}&FileType=json',
                formatter=parameters('DateFrom', 'DateTo')
            )
