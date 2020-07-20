from kingfisher_scrapy.spiders.portugal_base import PortugalBase


class PortugalRecords(PortugalBase):
    """
    Swagger API documentation
      https://www.base.gov.pt/swagger/index.html
    """
    name = 'portugal_records'
    data_type = 'record_package'
    url = 'https://www.base.gov.pt/api/Record/GetRecords?offset=1'
