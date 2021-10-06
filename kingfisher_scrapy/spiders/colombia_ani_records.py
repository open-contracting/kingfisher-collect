import scrapy
from kingfisher_scrapy.base_spider import SimpleSpider


class ColombiaANIRecords(SimpleSpider):
    """
    Domain
      Agencia Nacional de Infraestructura (ANI)
    API documentation
      https://apicost.azurewebsites.net/cost/records
    """
    name = 'colombia_ani_records'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        url = 'https://apicost.azurewebsites.net/cost/records'
        yield scrapy.Request(url, meta={'file_name': 'all.json'})
