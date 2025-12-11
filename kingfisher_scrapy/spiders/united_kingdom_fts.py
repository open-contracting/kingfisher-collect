from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class UnitedKingdomFTS(LinksSpider, PeriodicSpider):
    """
    Domain
      Find a Tender Service (FTS)
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2021-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format). Defaults to now.
    API documentation
      https://www.find-tender.service.gov.uk/apidocumentation/1.0/GET-ocdsReleasePackages
    """

    name = "united_kingdom_fts"
    custom_settings = {
        # The API (using Amazon ELB) eventually responds with HTTP 429 "12 request limit in 2 minute exceeded".
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 10,
    }

    # BaseSpider
    date_format = "datetime"
    default_from_date = "2021-01-01T00:00:00"
    max_attempts = 5
    # The API documentation describes 429 and 503, but 504 has also been observed.
    # https://www.find-tender.service.gov.uk/apidocumentation/1.0/GET-ocdsReleasePackages
    retry_http_codes = [429, 503, 504]

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(parameters("updatedTo"))
    next_link_formatter = staticmethod(parameters("cursor"))

    # PeriodicSpider
    pattern = (
        "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages?updatedFrom="
        "{0:%Y-%m-%dT%H:%M:%SZ}&updatedTo={1:%Y-%m-%dT%H:%M:%SZ}"
    )
    # The endpoint doesn't return all available releases with a longer `step` value.
    step = 1

    @handle_http_error
    def parse(self, response):
        # TODO(james): Temporary fix. Remove this method once the issue is closed in Kingfisher Process.
        # https://github.com/open-contracting/kingfisher-process/issues/323
        response = response.replace(body=response.body.replace(b"1e9999", b"9999999"))
        yield from super().parse(response)

    def get_retry_wait_time(self, response):
        return 30
