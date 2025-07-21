from kingfisher_scrapy.spiders.tanzania_bulk_base import TanzaniaBulkBase


class TanzaniaBulkRecords(TanzaniaBulkBase):
    """
    Domain
      Public Procurement Regulatory Authority (PPRA) NeST Data Portal
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2022-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Bulk download documentation
      https://data.nest.go.tz/ocds
    """

    name = "tanzania_bulk_records"

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # tanzania_bulk_releases

    # SimpleSpider
    data_type = "record_package"
