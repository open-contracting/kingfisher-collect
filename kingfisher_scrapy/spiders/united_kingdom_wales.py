from kingfisher_scrapy.spiders.proactis_base import ProactisBase


class UnitedKingdomWales(ProactisBase):
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
    name = 'united_kingdom_wales'

    # SimpleSpider
    data_type = 'release_package'

    # ProactisBase
    base_url = 'https://api.sell2wales.gov.wales'
    notice_types = [
        51,  # Site Notice - Website Invitation to Tender Notice
        52,  # Site Notice - Website Prior Information Notice
        53,  # Site Notice - Website Contract Award Notice
        54,  # Site Notice - Sub Contract Pre Award
        55,  # Site Notice - Sub Contract Post Award
        56,  # Site Notice - Sub Contract Award
    ]
