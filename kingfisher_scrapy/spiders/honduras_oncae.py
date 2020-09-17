from os.path import split
from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasONCAE(CompressedFileSpider):
    """
    Bulk download documentation
      http://oncae.gob.hn/datosabiertos
    Spider arguments
      system
        Download only data from the provided system.
        ``HC1`` for "HonduCompras 1.0 - Módulo de Difusión de Compras y Contrataciones" system.
        ``CE`` for "Módulo de Difusión Directa de Contratos" system.
        ``DDC`` for "Catálogo Electrónico" system.
      sample
        Downloads the first package listed on the downloads page for each system.
        If ``system'' is also provided, a single package is downloaded from that system.
    """
    name = 'honduras_oncae'
    data_type = 'release_package'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    systems = ['HC1', 'CE', 'DDC']

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        if hasattr(spider, 'system') and spider.system not in spider.systems:
            raise scrapy.exceptions.CloseSpider('Specified system is not recognized')
        return spider

    def start_requests(self):
        yield scrapy.Request(
            'http://oncae.gob.hn/datosabiertos',
            meta={'file_name': 'list.html'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        systems_flags = {system: False for system in self.systems}
        urls = response.xpath('//a[contains(., "[json]")]/@href').getall()
        for url in urls:
            path, file = split(urlparse(url).path)
            current_system = path.replace('/datosabiertos/', "")
            if hasattr(self, 'system') and current_system != self.system:
                continue
            if self.sample:
                if systems_flags[current_system]:
                    continue
                if next((system for system in systems_flags if not system), False):
                    return
                systems_flags[current_system] = True
            # URL looks like http://200.13.162.79/datosabiertos/HC1/HC1_datos_2020_json.zip
            yield self.build_request(url, formatter=components(-1))
