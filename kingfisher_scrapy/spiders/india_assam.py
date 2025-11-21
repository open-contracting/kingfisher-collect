from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components

# curl https://www.data.gov.in/files/ogdpv2dms/s3fs-public/ocds_mapped_procurement_data_fiscal_year_2022_2023.csv


class IndiaAssam(PeriodicSpider):
    """
    Domain
      Assam State Government Finance Department
    Caveats
      This dataset was last updated by the publisher in 2022.
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2016'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    Bulk download documentation
      https://data.gov.in/catalog/assam-public-procurement-data
    """

    name = "india_assam"

    # To avoid 403 errors when unflattening the CSV files.
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
    }

    # BaseSpider
    unflatten = True

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    date_format = "year"
    formatter = staticmethod(components(-1))  # filename containing year
    default_from_date = "2016"
    default_until_date = "2021"

    def build_urls(self, date):
        yield (
            "https://www.data.gov.in/files/ogdpv2dms/s3fs-public/ocds_mapped_procurement_data_fiscal_year_"
            f"{date}_{date + 1}.csv"
        )
