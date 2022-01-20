from datetime import timedelta

from kingfisher_scrapy.base_spiders.simple_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class Kosovo(SimpleSpider):
    """
    Domain
      Public Procurement Regulatory Commission
    Spider arguments
      from_date
        Download only data with a tender period end date from this time onward (YYYY-MM-DD format).
        Defaults to '2000-01-01'.
      until_date
        Download only data with a tender period end date until this time (YYYY-MM-DD format). Defaults to now.
        Note: This date is non-inclusive.
    API documentation
      https://ocdskrpp.rks-gov.net/Help
    """
    name = 'kosovo'

    # BaseSpider
    date_format = 'date'
    date_required = True
    default_from_date = '2000-01-01'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # The API is slow even with short periods, so we request one day at a time.
        delta = self.until_date - self.from_date
        for days in reversed(range(delta.days + 1)):
            start = self.from_date + timedelta(days=days - 1)
            end = self.from_date + timedelta(days=days)
            url = 'https://ocdskrpp.rks-gov.net/krppapi/tenderrelease?endDateFrom=' \
                  f'{start.strftime("%Y-%m-%d")}&endDateEnd={end.strftime("%Y-%m-%d")}'

            yield self.build_request(url, formatter=parameters('endDateFrom', 'endDateEnd'))

    @handle_http_error
    def parse(self, response):
        data = response.json()
        # The API returns a release package with an empty releases array if no releases were found.
        if data['releases']:
            yield self.build_file_from_response(response, data_type=self.data_type)
