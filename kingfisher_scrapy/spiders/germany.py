from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import parameters


class Germany(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      The Procurement Office of the Federal Ministry of the Interior (BMI) - Bekanntmachungsservice: OpenData API
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2022-04'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    Swagger API documentation
      https://www.oeffentlichevergabe.de/documentation/swagger-ui/opendata/index.html
    """
    name = 'germany'

    # CompressedFileSpider
    data_type = 'release'

    # PeriodicSpider
    date_format = 'year-month'
    default_from_date = '2022-04'
    formatter = staticmethod(parameters('pubMonth', 'format'))
    pattern = 'https://www.oeffentlichevergabe.de/api/notice-exports?pubMonth={0.year:d}-{0.month:02d}&format=ocds.zip'
