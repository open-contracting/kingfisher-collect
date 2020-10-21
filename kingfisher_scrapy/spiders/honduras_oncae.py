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
        If ``system`` is also provided, the set number of release packages is downloaded from that system.
    """
    name = 'honduras_oncae'
    data_type = 'release_package'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    available_systems = ['HC1', 'CE', 'DDC']

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, system=system, *args, **kwargs)
        if system and spider.system not in spider.available_systems:
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
        urls = response.xpath('//a[contains(., "[json]")]/@href').getall()
        for url in urls:
            path, file = urlparse(url).path.rsplit('/', 1)
            current_system = path.replace('/datosabiertos/', "")
            if self.system and current_system != self.system:
                continue
            # URL looks like http://200.13.162.79/datosabiertos/HC1/HC1_datos_2020_json.zip
            yield self.build_request(url, formatter=components(-1))
