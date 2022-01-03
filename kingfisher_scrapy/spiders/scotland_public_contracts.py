from datetime import date

from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import parameters


class ScotlandPublicContracts(PeriodicSpider):
    """
    Domain
      Public Contracts Scotland
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to a year ago.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://api.publiccontractsscotland.gov.uk/v1
    """
    name = 'scotland_public_contracts'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = date(date.today().year - 1, date.today().month, 1)

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom={:%m-%Y}&outputType=0&noticeType={}'
    formatter = staticmethod(parameters('noticeType', 'dateFrom'))

    notice_types = [
        1,  # OJEU - F1 - Prior Information Notice
        2,  # OJEU - F2 - Contract Notice
        3,  # OJEU - F3 - Contract Award Notice
        4,  # OJEU - F4 - Prior Information Notice(Utilities)
        5,  # OJEU - F5 - Contract Notice(Utilities)
        6,  # OJEU - F6 - Contract Award Notice(Utilities)
        7,  # OJEU - F7 - Qualification Systems(Utilities)
        12,  # OJEU - F12 - Design Contest Notice
        13,  # OJEU - F13 - Results Of Design Contest
        14,  # OJEU - F14 - Corrigendum
        15,  # OJEU - F15 - Voluntary Ex Ante Transparency Notice
        20,  # OJEU - F20 - Modification Notice
        21,  # OJEU - F21 - Social And other Specific Services(Public Contracts)
        22,  # OJEU - F22 - Social And other Specific Services(Utilities)
        23,  # OJEU - F23 - Social And other Specific Services(Concessions)
        24,  # OJEU - F24 - Concession Notice
        25,  # OJEU - F25 - Concession Award Notice
        101,  # Site Notice - Website Contract Notice
        102,  # Site Notice - Website Prior Information Notice
        103,  # Site Notice - Website Contract Award Notice
        104,  # Site Notice - Quick Quote Award
    ]

    def build_urls(self, date):
        for notice_type in self.notice_types:
            yield self.pattern.format(date, notice_type)

    def parse(self, response):
        data = response.json()
        # Some responses are a package without a list of releases.
        if 'releases' not in data:
            yield self.build_file_error_from_response(response, errors=data)
        else:
            yield from super().parse(response)
