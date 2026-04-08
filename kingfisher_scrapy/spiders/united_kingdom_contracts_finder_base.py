from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import parameters, transcode_bytes


class UnitedKingdomContractsFinderBase(LinksSpider, PeriodicSpider):
    custom_settings = {
        # The API has unpredictable and undocumented "too many requests" logic.
        "CONCURRENT_REQUESTS": 1,
    }

    # BaseSpider
    date_format = "datetime"
    default_from_date = "2014-01-01T00:00:00"
    encoding = "iso-8859-1"
    # "When the user has submitted too many requests, no further requests should be made until after 5 minutes"
    # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
    retry_http_codes = [403]

    # LinksSpider
    formatter = staticmethod(parameters("publishedFrom", "publishedTo"))
    next_link_formatter = staticmethod(parameters("publishedFrom", "publishedTo", "cursor"))

    # PeriodicSpider
    pattern = (
        "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
        "?limit=100&publishedFrom={0:%Y-%m-%d}&publishedTo={1:%Y-%m-%d}"
    )
    start_callback = "parse_page"
    step = 15

    # parse_page must be provided by subclasses.

    # LinksSpider
    def parse(self, response):
        # Remove non-iso-8859-1 characters.
        yield from super().parse(response.replace(body=transcode_bytes(response.body, self.encoding)))

    # BaseSpider
    def get_retry_wait_time(self, response):
        return 300
