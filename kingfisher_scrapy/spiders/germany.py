from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import parameters


class Germany(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Bekanntmachungsservice - Procurement Office of the Federal Ministry of the Interior (BMI)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2022-12'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    Swagger API documentation
      https://www.oeffentlichevergabe.de/documentation/swagger-ui/opendata/index.html
    """

    name = "germany"

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2022-12"

    # CompressedFileSpider
    data_type = "release_package"

    # PeriodicSpider
    pattern = "https://www.oeffentlichevergabe.de/api/notice-exports?pubMonth={0:%Y}-{0:%m}&format=ocds.zip"
    formatter = staticmethod(parameters("pubMonth", "format"))
