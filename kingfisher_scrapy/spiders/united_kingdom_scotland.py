from kingfisher_scrapy.spiders.proactis_base import ProactisBase


class UnitedKingdomScotland(ProactisBase):
    """
    Domain
      Public Contracts Scotland
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2019-01'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://api.publiccontractsscotland.gov.uk/v1
    Bulk download documentation
      https://www.publiccontractsscotland.gov.uk/NoticeDownload/Download.aspx
    """
    name = 'united_kingdom_scotland'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    default_from_date = '2019-01'

    # ProactisBase
    base_url = 'https://api.publiccontractsscotland.gov.uk'
    notice_types = [
        101,  # Site Notice - Website Contract Notice
        102,  # Site Notice - Website Prior Information Notice
        103,  # Site Notice - Website Contract Award Notice
        104,  # Site Notice - Quick Quote Award
    ]
