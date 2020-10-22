import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasPortalBulkFiles(SimpleSpider):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      publisher
        Filter by publisher:

        oncae
          Oficina Normativa de Contratación y Adquisiciones del Estado
        sefin
          Secretaria de Finanzas de Honduras
    Bulk download documentation
      http://www.contratacionesabiertas.gob.hn/descargas/
    """
    name = 'honduras_portal_bulk_files'
    data_type = 'release_package'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    publishers = {'oncae': 'ONCAE', 'sefin': 'Secretaria de Finanzas'}

    @classmethod
    def from_crawler(cls, crawler, publisher=None, *args, **kwargs):
        spider = super().from_crawler(crawler, publisher=publisher, *args, **kwargs)
        if publisher and publisher not in spider.publishers:
            raise scrapy.exceptions.CloseSpider('Specified publisher is not recognized')

        spider.publisher_name = spider.publishers.get(publisher)

        return spider

    def start_requests(self):
        yield scrapy.Request(
            'http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json',
            meta={'file_name': 'list.json'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        items = json.loads(response.text)
        for item in items:
            if self.publisher and self.publisher_name not in item['publicador']:
                continue
            url = item['urls']['json']
            yield self.build_request(url, formatter=components(-1))
