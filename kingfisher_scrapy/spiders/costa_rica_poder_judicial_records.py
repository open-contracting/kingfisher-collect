import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class CostaRicaPoderJudicialRecords(SimpleSpider):
    """
    Domain
      Poder Judicial de Costa Rica
    Bulk download documentation
      http://datosabiertospj.eastus.cloudapp.azure.com/dataset/estandar-de-datos-de-contrataciones-abiertas-ocds
    """

    name = 'costa_rica_poder_judicial_records'
    data_type = 'record_package'

    def start_requests(self):
        url = 'http://datosabiertospj.eastus.cloudapp.azure.com/api/3/action/package_show?id=estandar-de-datos-de' \
              '-contrataciones-abiertas-ocds'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for resource in data['result']['resources']:
            if resource['format'].upper() == 'JSON':
                yield self.build_request(resource['url'], formatter=components(-1))
