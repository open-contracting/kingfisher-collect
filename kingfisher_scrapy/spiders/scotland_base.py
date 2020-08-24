from datetime import date

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import date_range_by_month, parameters


class ScotlandBase(SimpleSpider):
    default_from_date = '2019-01'
    date_format = 'year-month'

    @classmethod
    def from_crawler(cls, crawler, from_date=None, *args, **kwargs):
        if not from_date:
            from_date = cls.default_from_date

        return super().from_crawler(crawler, from_date=from_date, *args, **kwargs)

    def start_requests(self):
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

        for year_month in date_range_by_month(self.from_date, date.today()):
            date_string = year_month.strftime('%m-%Y')
            for notice_type in notice_types:
                yield self.build_request(
                    self.url.format(date_string, notice_type),
                    formatter=parameters('noticeType', 'dateFrom')
                )
            if self.sample:
                return
