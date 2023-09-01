from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components


class IndiaAssamFinanceDepartment(PeriodicSpider):
    """
    Domain
      Assam State Government Finance Department - Open Government Data (OGD) Platform India
    Bulk download documentation
      https://data.gov.in/catalog/assam-public-procurement-data
    """
    name = 'india_assam_finance_department'

    # BaseSpider
    unflatten = True

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    date_format = 'year'
    formatter = staticmethod(components(-1))
    default_from_date = '2016'
    default_until_date = '2021'

    def build_urls(self, date):
        """
        Yields one or more URLs for the given date.
        """
        url = 'https://data.gov.in/files/ogdpv2dms/s3fs-public/ocds_mapped_procurement_data_fiscal_year'
        yield f'{url}_{date}_{date+1}.csv'
