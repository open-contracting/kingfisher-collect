from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
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
        Download only data until this year (YYYY format). Defaults to the current year.
      system
        Filter by system:

        CE
          Catálogo Electrónico
        DDC
          Módulo de Difusión Directa de Contratos
        HC1
          HonduCompras 1.0 (Módulo de Difusión de Compras y Contrataciones)
    Bulk download documentation
      https://oncae.gob.hn/datosabiertos
    """
    name = 'honduras_oncae'
    download_timeout = 900

    # BaseSpider
    date_format = 'year'
    default_from_date = '2005'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases

    # SimpleSpider
    data_type = 'release_package'

    # CompressedFileSpider
    yield_non_archive_file = True

    # PeriodicSpider
    pattern = 'https://datosabiertos.oncae.gob.hn/datosabiertos/{}'
    formatter = staticmethod(components(-1))  # year

    # Local
    available_systems = ['HC1', 'CE', 'DDC']

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
            if system == 'HC1':
                suffix = f'{date}.json'
            else:
                suffix = f'{date}_json.zip'
            yield self.pattern.format(f"{system}/{system}_datos_{suffix}")
