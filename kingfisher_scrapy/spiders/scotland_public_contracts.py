from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandPublicContracts(ScotlandBase):
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

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom={:%m-%Y}&outputType=0&noticeType={}'
