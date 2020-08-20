from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandPublicContracts(ScotlandBase):
    """
    API documentation
      https://api.publiccontractsscotland.gov.uk/v1
    Spider arguments
      sample
        Download this month's release packages for each notice type available.
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2019-01'.
    """
    name = 'scotland_public_contracts'
    data_type = 'release_package'
    url = 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom={}&outputType=1&noticeType={}'
