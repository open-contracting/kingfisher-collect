import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasPortalBulkFiles(SimpleSpider):
    """
    Bulk download documentation
      http://www.contratacionesabiertas.gob.hn/descargas/
    Spider arguments
      sample
        Downloads the first package listed in http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json.
    """
    name = 'honduras_portal_bulk_files'
    data_type = 'release_package'
    skip_latest_release_date = 'Already covered (see code for details)'  # honduras_portal_releases

    def start_requests(self):
        yield scrapy.Request(
            'http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json',
            meta={'file_name': 'list.json'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        items = json.loads(response.text)
        if self.sample:
            items = [items[0]]

        for item in items:
            url = item['urls']['json']
            yield self.build_request(url, formatter=components(-1))
