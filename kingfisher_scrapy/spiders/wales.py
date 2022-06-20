from kingfisher_scrapy.spiders.proactis_base import ProactisBase


class Wales(ProactisBase):
    """
    Domain
      Wales
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to a year ago.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://api.sell2wales.gov.wales/v1
    Bulk download documentation
      https://www.sell2wales.gov.wales/Notice/Download/Download.aspx
    """
    name = 'wales'

    # SimpleSpider
    data_type = 'release_package'

    url_base = 'https://api.sell2wales.gov.wales'

    notice_types = [
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
        51,  # Site Notice - Website Invitation to Tender Notice
        52,  # Site Notice - Website Prior Information Notice
        53,  # Site Notice - Website Contract Award Notice
        54,  # Site Notice - Sub Contract Pre Award
        55,  # Site Notice - Sub Contract Post Award
        56,  # Site Notice - Sub Contract Award
    ]
