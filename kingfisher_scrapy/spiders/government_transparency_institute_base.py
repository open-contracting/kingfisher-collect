from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, components


class GovernmentTransparencyInstituteBase(CompressedFileSpider):
    """
    Domain
      Government Transparency Institute
    Bulk download documentation
      https://opentender.eu/download
    """

    user_agent = BROWSER_USER_AGENT  # to avoid HTTP 410

    # BaseSpider
    line_delimited = True

    # CompressedFileSpider
    data_type = "release_package"

    # Local
    base_url = "https://opentender.eu/data/downloads/data-{}-{}-json.zip"
    infix = "ocds"

    # country_code must be provided by subclasses.

    def start_requests(self):
        yield self.build_request(self.base_url.format(self.country_code, self.infix), formatter=components(-1))
