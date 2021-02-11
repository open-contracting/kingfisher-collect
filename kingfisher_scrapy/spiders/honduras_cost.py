import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class HondurasCoST(SimpleSpider):
    """
    Domain
      Systema de Información y Seguimiento de Obras y Contratos (SISOCS)
    """
    name = 'honduras_cost'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        # Extracted from http://app.sisocs.org/protected/ocdsShow/
        yield scrapy.Request('http://67.207.88.38:8080/sisocs/records', meta={'file_name': 'all.json'})
