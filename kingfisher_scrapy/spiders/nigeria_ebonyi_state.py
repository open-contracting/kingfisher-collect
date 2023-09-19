from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error


class NigeriaEbonyiState(PeriodicSpider):
    """
    Domain
      Ebonyi E-PROCUREMENT
    Caveats
        The JSON data sometimes contains unescaped tab characters within strings.
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2018'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://ebonyieprocure.eb.gov.ng/ocds_report.php
    """
    name = 'nigeria_ebonyi_state'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2018'

    # PeriodicSpider
    pattern = 'http://ebonyieprocure.eb.gov.ng/media/ocds{}.json'
    formatter = staticmethod(components(-1))  # filename containing year

    # SimpleSpider
    data_type = 'release_package'

    @handle_http_error
    def parse(self, response):
        # Replace unescaped tab characters within strings with a space.
        response = response.replace(body=response.body.replace(b'\t', b' '))
        yield from super().parse(response)
