import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class ColombiaANIRecords(SimpleSpider):
    """
    Domain
      Agencia Nacional de Infraestructura (ANI)
    Caveats
      This dataset was last updated by the publisher in 2021.
    Bulk download documentation
      https://aniscopio.ani.gov.co/datos-abiertos
    API endpoints
      Get all records
        Link
          ``https://apicost.azurewebsites.net/cost/records``
    """

    name = "colombia_ani_records"

    # SimpleSpider
    data_type = "record_package"

    def start_requests(self):
        # Extracted from https://aniscopio.ani.gov.co/datos-abiertos, 'OCDS' tab
        url = "https://apicost.azurewebsites.net/cost/records"
        yield scrapy.Request(url, meta={"file_name": "all.json"})
