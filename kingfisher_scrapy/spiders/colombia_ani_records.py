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

    async def start(self):
        # Extracted from https://aniscopio.ani.gov.co/datos-abiertos, 'OCDS' tab
        yield scrapy.Request("https://apicost.azurewebsites.net/cost/records", meta={"file_name": "all.json"})
