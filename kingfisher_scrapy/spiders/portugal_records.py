from kingfisher_scrapy.spiders.portugal_base import PortugalBase


class PortugalRecords(PortugalBase):
    """
    Swagger API documentation
      http://www.base.gov.pt/swagger/index.html
    Spider arguments
      sample
        Download only one record.
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2010-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    """
    name = 'portugal_records'
    data_type = 'record_package_json_lines'
    url = 'http://www.base.gov.pt/api/Record/GetRecords?offset=1'
