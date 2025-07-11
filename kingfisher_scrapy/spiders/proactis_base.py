from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class ProactisBase(PeriodicSpider):
    # BaseSpider
    date_format = "year-month"

    # PeriodicSpider
    pattern = "/v1/Notices?dateFrom={:%m-%Y}&outputType=0&noticeType={}"
    formatter = staticmethod(parameters("noticeType", "dateFrom"))

    # base_url and notice_types must be provided by subclasses.

    # Local
    base_notice_types = [
        1,  # OJEU - F1 - Prior Information Notice
        2,  # OJEU - F2 - Contract Notice
        3,  # OJEU - F3 - Contract Award Notice
        4,  # OJEU - F4 - Prior Information Notice (Utilities)
        5,  # OJEU - F5 - Contract Notice (Utilities)
        6,  # OJEU - F6 - Contract Award Notice (Utilities)
        7,  # OJEU - F7 - Qualification Systems (Utilities)
        12,  # OJEU - F12 - Public design contest
        13,  # OJEU - F13 - Results of Design Contest
        14,  # OJEU - F14 - Corrigendum
        15,  # OJEU - F15 - Voluntary Ex Ante Transparency Notice
        20,  # OJEU - F20 - Modification Notice
        21,  # OJEU - F21 - Social And other Specific Services (Public Contracts)
        22,  # OJEU - F22 - Social and other specific services (Utilities)
        23,  # OJEU - F23 - Social and other specific services (Concessions)
        24,  # OJEU - F24 - Concession Notice
        25,  # OJEU - F25 - Concession Award Notice
    ]

    def build_urls(self, date):
        url = self.base_url + self.pattern
        self.base_notice_types.extend(self.notice_types)

        for notice_type in self.base_notice_types:
            yield url.format(date, notice_type)

    @handle_http_error
    def parse(self, response):
        data = response.json()

        # Some responses are a package without a list of releases.
        if "releases" not in data:
            self.log_error_from_response(response, level="warning", message=data)
            return

        yield from super().parse(response)
