import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasPortalBulkFiles(SimpleSpider):
    """
    Bulk download documentation
      http://www.contratacionesabiertas.gob.hn/descargas/
    Spider arguments
      publisher
        Filter the data by a specific publisher.
        ``oncae`` for "Oficina Normativa de Contratación y Adquisiciones del Estado" publisher.
        ``sefin`` for "Secretaria de Finanzas de Honduras" publisher.
      sample
        Downloads the first package listed in http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json.
        If ``publisher'' is also provided, a single package is downloaded from that publisher.
    """
    name = 'honduras_portal_bulk_files'
    data_type = 'release_package'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    publishers = ['oncae', 'sefin']

    @classmethod
    def from_crawler(cls, crawler, publisher=None, *args, **kwargs):
        spider = super().from_crawler(crawler, publisher=publisher, *args, **kwargs)
        if publisher and publisher not in spider.publishers:
            raise scrapy.exceptions.CloseSpider('Specified publisher is not recognized')

        if publisher == 'oncae':
            spider.publisher_filter = 'ONCAE'
        elif publisher == 'sefin':
            spider.publisher_filter = 'Secretaria de Finanzas'

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
            if self.publisher and self.publisher_filter not in item['publicador']:
                continue
            url = item['urls']['json']
            yield self.build_request(url, formatter=components(-1))

            if self.sample:
                return
