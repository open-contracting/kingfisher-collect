import datetime

import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class UnitedKingdomFTS(LinksSpider):
    """
    Domain
      Find a Tender Service (FTS)
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
        If ``until_date`` is provided, defaults to '2021-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format).
        If ``from_date`` is provided, defaults to now.
    API documentation
      https://www.find-tender.service.gov.uk/apidocumentation/1.0/GET-ocdsReleasePackages
    """

    name = "united_kingdom_fts"

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
    formatter = staticmethod(parameters("cursor"))

    def start_requests(self):
        url = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            url = f"{url}?updatedFrom={from_date}&updatedTo={until_date}"
        else:
            until_date = datetime.datetime.now(tz=datetime.timezone.utc).strftime(self.date_format)
        yield scrapy.Request(url, meta={"file_name": f"{until_date}.json"}, headers={"Accept": "application/json"})

    @handle_http_error
    def parse(self, response):
        # TODO(james): Temporary fix. Remove this method once the issue is closed in Kingfisher Process.
        # https://github.com/open-contracting/kingfisher-process/issues/323
        response = response.replace(body=response.body.replace(b"1e9999", b"9999999"))
        yield from super().parse(response)

    def get_retry_wait_time(self, response):
        # 504 responses do not set the Retry-After header.
        if response.status == 504:
            return 30
        return super().get_retry_wait_time(response)
