from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import get_parameter_value, parameters, replace_parameters


class UgandaReleases(PeriodicSpider):
    """
    Domain
      Government Procurement Portal (GPP) - Public Procurement and Disposal of Public Assets Authority (PPDA)
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

    name = "uganda_releases"
    # https://gpp.ppda.go.ug/public/open-data/ocds/ocds-datasets generates URLs with JavaScript. We increment
    # the 'code' parameter until it 404s. As such, we can't disambiguate expected from unexpected 404s.
    handle_httpstatus_list = [404]
    # Returns HTTP 403 if too many requests. (1 is too short.)
    download_delay = 2

    # BaseSpider
    date_format = "year"
    default_from_date = "2019"

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    pattern = "https://cdn.ppda.go.ug/api/open-data/v2/ocds/download?fy={0}-{1}&format=json&code=1"
    formatter = staticmethod(parameters("fy", "code"))

    # PeriodicSpider
    def build_urls(self, date):
        yield self.pattern.format(date, date + 1)

    # SimpleSpider
    def parse(self, response):
        # 404 responses indicate we've reached the end of the 'code' sequence for this fiscal year.
        if response.status == 404:
            return

        yield from super().parse(response)

        yield self.build_request(
            replace_parameters(response.request.url, code=int(get_parameter_value(response.request.url, "code")) + 1),
            formatter=self.formatter,
        )
