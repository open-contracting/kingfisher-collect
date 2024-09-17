import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components, handle_http_error


class HondurasIAIP(SimpleSpider):
    """
    Domain
      Instituto de Acceso a la Información Publica (IAIP)
    Spider arguments
      portal
        Filter by portal:

          covid19
            IAIP Emergencia Covid-19
          huracanes
            Emergencia Huracán ETA
          oficio
            Portal Único de Transparencia
    Bulk download documentation
      https://portalunico.iaip.gob.hn/datosabierto/
    """

    name = 'honduras_iaip'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    available_portals = ['covid19', 'huracanes', 'oficio']

    @classmethod
    def from_crawler(cls, crawler, portal=None, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, portal=portal, **kwargs)
        if portal and spider.portal not in spider.available_portals:
            raise SpiderArgumentError(f'spider argument `portal`: {spider.portal!r} not recognized')
        return spider

    def start_requests(self):
        yield scrapy.Request(
            'https://www.contratacionesabiertas.gob.hn/api/v1/iaip_datosabiertos/?format=json',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        for portal in self.available_portals:
            if self.portal and self.portal != portal:
                continue
            # Each portal is an array of objects with the filename and its CSV, Excel and JSON URL representations:
            #
            # "portal": [ {"nombreArchivo": "name", "excel": "URL", "csv": "URL", "json": "URL"} ]
            for item in response.json()[portal]:
                url = item['json']
                # Retrieve URLs for packages of individual releases, not of compiled releases.
                if 'compiled' not in url.lower():
                    yield self.build_request(url, formatter=components(-1))
