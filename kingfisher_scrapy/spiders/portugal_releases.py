from kingfisher_scrapy.spiders.portugal_base import PortugalBase


class PortugalReleases(PortugalBase):
    """
    Swagger API documentation
      https://www.base.gov.pt/swagger/index.html
    """
    name = 'portugal_releases'
    data_type = 'release_package'
    url = 'https://www.base.gov.pt/api/Release/GetReleases?offset=1'
