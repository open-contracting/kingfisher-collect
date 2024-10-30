from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import browser_user_agent, components


class GovernmentTransparencyInstituteBase(CompressedFileSpider):
    """
    Domain
      Government Transparency Institute
    Bulk download documentation
      https://opentender.eu/download
    """

    user_agent = browser_user_agent  # to avoid HTTP 410 error

    # BaseSpider
    line_delimited = True

    # CompressedFileSpider
    data_type = 'release_package'

    # Local
    base_url = 'https://opentender.eu/data/downloads/data-{}-json-json.zip'

    # country_code must be provided by subclasses.

    def start_requests(self):
        yield self.build_request(self.base_url.format(self.country_code), formatter=components(-1))
