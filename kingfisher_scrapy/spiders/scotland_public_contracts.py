from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandPublicContracts(ScotlandBase):
    """
    API documentation
      https://api.publiccontractsscotland.gov.uk/v1
    Spider arguments
      sample
        Downloads packages for releases dated one year ago, for each notice type available.
    """
    name = 'scotland_public_contracts'
    data_type = 'release_package'

    def start_requests(self):
        pattern = 'https://api.publiccontractsscotland.gov.uk/v1/Notices?dateFrom={}&outputType=1&noticeType={}'
        return self.parse_requests(pattern)
