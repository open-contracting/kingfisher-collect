from kingfisher_scrapy.spiders.proactis_base import ProactisBase


class ScotlandPublicContracts(ProactisBase):
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
    Bulk download documentation
      https://www.publiccontractsscotland.gov.uk/NoticeDownload/Download.aspx
    """
    name = 'scotland_public_contracts'

    # SimpleSpider
    data_type = 'release_package'

    url_base = 'https://api.publiccontractsscotland.gov.uk'

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
