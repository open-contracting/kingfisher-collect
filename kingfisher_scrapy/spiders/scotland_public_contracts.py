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

    # ProactisBase
    base_url = 'https://api.publiccontractsscotland.gov.uk'

    notice_types = [
        101,  # Site Notice - Website Contract Notice
        102,  # Site Notice - Website Prior Information Notice
        103,  # Site Notice - Website Contract Award Notice
        104,  # Site Notice - Quick Quote Award
    ]
