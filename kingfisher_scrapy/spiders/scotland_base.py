from datetime import date

from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import parameters


class ScotlandBase(PeriodicSpider):
    date_format = 'year-month'
    default_from_date = date(date.today().year - 1, date.today().month, 1)

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

    def build_urls(self, pattern, date):
        for notice_type in self.notice_types:
            yield pattern.format(date, notice_type)

    def get_formatter(self):
        return parameters('noticeType', 'dateFrom')
