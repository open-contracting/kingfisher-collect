from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandPublicContracts(ScotlandBase):
    """
    API documentation
      https://api.publiccontractsscotland.gov.uk/v1
    Spider arguments
      sample
        Sets the number of release packages to download.
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2019-01'.
    """
    name = 'scotland_public_contracts'
    data_type = 'release_package'
    pattern = 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom={:%m-%Y}&outputType=0&noticeType={}'
