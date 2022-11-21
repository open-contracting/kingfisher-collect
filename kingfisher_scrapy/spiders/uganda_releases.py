from urllib.parse import parse_qs, urlparse

from scrapy.settings.default_settings import RETRY_HTTP_CODES

from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import parameters


class UgandaReleases(PeriodicSpider):
    """
    Domain
      Government Procurement Portal (GPP) of Public Procurement and Disposal of Public Assets Authority (PPDA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2019'.
        The year refers to the start of the fiscal year range, e.g. if ``from_date`` = '2019' then the fiscal year is
        '2019-2020'
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
        The year refers to the start of the fiscal year range, e.g. if ``until_date`` = '2019' then the fiscal year is
        '2019-2020'
    Bulk download documentation
        https://gpp.ppda.go.ug/public/open-data/ocds/ocds-datasets
    """
    name = 'uganda_releases'
    custom_settings = {
        # We cannot get the list of all the files from https://gpp.ppda.go.ug/public/open-data/ocds/ocds-datasets
        # because the list is generated in the browser.
        # To get all the files, we follow the pattern download?fy={0}-{1}&code=1, iterating de 'code' value until it
        # returns HTTP 500 error FileNotFoundException. Therefore, we retry all codes but 500
        'RETRY_HTTP_CODES': filter(lambda status: status != 500, RETRY_HTTP_CODES),
    }
    # BaseSpider
    date_format = 'year'
    default_from_date = '2019'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    formatter = staticmethod(parameters('fy', 'code'))
    pattern = 'https://gpp.ppda.go.ug/adminapi/public/api/open-data/v2/ocds/download?fy={0}-{1}&code=1'
    start_requests_callback = 'build_next'

    def build_next(self, response):
        if response.status == 500:
            return
        elif not self.is_http_success(response):
            yield self.build_file_error_from_response(response)
        else:
            yield from super().parse(response)
            next_code = int(parse_qs(urlparse(response.request.url).query)['code'][0])+1
            yield self.build_request(f"{response.request.url.split('code=')[0]}code={next_code}",
                                     formatter=self.formatter, callback=self.build_next)

    def build_urls(self, date):
        """
        Yields one or more URLs for the given date.
        """
        yield self.pattern.format(date, date+1)
