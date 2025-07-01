from kingfisher_scrapy.spiders.tanzania_api_base import TanzaniaAPIBase


class TanzaniaAPIRecords(TanzaniaAPIBase):
    """
    Domain
      Public Procurement Regulatory Authority (PPRA) NeST Data Portal
    API documentation
      https://data.nest.go.tz/ocds
    """

    name = 'tanzania_api_records'

    # SimpleSpider
    data_type = 'record'
