from kingfisher_scrapy.base_spider import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components


class HondurasONCAE(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2005'.
      until_date
        Download only data until this year (YYYY format). Defaults to current year.
      system
        Filter by system:

        CE
          Catálogo Electrónico
        DDC
          Módulo de Difusión Directa de Contratos
        HC1
          HonduCompras 1.0 (Módulo de Difusión de Compras y Contrataciones)
    Bulk download documentation
      http://oncae.gob.hn/datosabiertos
    """
    name = 'honduras_oncae'
    data_type = 'release_package'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    available_systems = ['HC1', 'CE', 'DDC']

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    # PeriodicSpider variables
    date_format = 'year'
    default_from_date = '2005'
    pattern = 'http://200.13.162.79/datosabiertos/{}'

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, system=system, *args, **kwargs)
        if system and spider.system not in spider.available_systems:
            raise SpiderArgumentError(f'spider argument `system`: {spider.system!r} not recognized')
        return spider

    def build_urls(self, date):
        for system in self.available_systems:
            if self.system and system != self.system:
                continue
            yield self.pattern.format(f"{system}/{system}_datos_{date}_json.zip")

    def get_formatter(self):
        return components(-1)
