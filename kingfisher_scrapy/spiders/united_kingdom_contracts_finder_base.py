from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import handle_http_error, parameters, transcode_bytes


class UnitedKingdomContractsFinderBase(LinksSpider, PeriodicSpider):
    # The API has unpredictable and undocumented "too many requests" logic.
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
    }

    # BaseSpider
    date_format = "datetime"
    default_from_date = "2014-01-01T00:00:00"
    encoding = "iso-8859-1"
    max_attempts = 5
    retry_http_codes = [403]

    # PeriodicSpider
    formatter = staticmethod(parameters("publishedFrom", "publishedTo"))
    next_link_formatter = staticmethod(parameters("publishedFrom", "publishedTo", "cursor"))
    start_callback = "parse_page"
    step = 15
    pattern = (
        "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
        "?limit=100&publishedFrom={0:%Y-%m-%d}&publishedTo={1:%Y-%m-%d}"
    )

    # parse_page must be provided by subclasses.

    @handle_http_error
    def parse(self, response):
        # Remove non-iso-8859-1 characters.
        response = response.replace(body=transcode_bytes(response.body, self.encoding))
        yield from super().parse(response)

    def get_retry_wait_time(self, response):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
        return 300
