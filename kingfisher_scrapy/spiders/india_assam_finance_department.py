from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components


class IndiaAssamFinanceDepartment(PeriodicSpider):
    """
    Domain
      Assam State Government Finance Department - Open Government Data (OGD) Platform India
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2016'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    Bulk download documentation
      https://data.gov.in/catalog/assam-public-procurement-data
    """
    name = 'india_assam_finance_department'

    # To avoid 403 errors when unflattening the CSV files.
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    unflatten = True

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    date_format = 'year'
    formatter = staticmethod(components(-1))  # filename containing year
    default_from_date = '2016'
    default_until_date = '2021'

    def build_urls(self, date):
        """
        Yields one or more URLs for the given date.
        """
        url = 'https://data.gov.in/files/ogdpv2dms/s3fs-public/ocds_mapped_procurement_data_fiscal_year'
        yield f'{url}_{date}_{date + 1}.csv'
