from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components


class HondurasPortalBulkFiles(PeriodicSpider):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2005-11'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
      publisher
        Filter by publisher:

        oncae
          Oficina Normativa de Contratación y Adquisiciones del Estado
        sefin
          Secretaria de Finanzas de Honduras
      system
        Filter by oncae system:

        CE
          Catálogo Electrónico
        DDC
          Módulo de Difusión Directa de Contratos
        HC1
          HonduCompras 1.0 (Módulo de Difusión de Compras y Contrataciones)
    Bulk download documentation
      http://www.contratacionesabiertas.gob.hn/descargas/
    """
    name = 'honduras_portal_bulk_files'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2005-11'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'http://www.contratacionesabiertas.gob.hn/api/v1/descargas/{}'

    available_publishers = {'oncae': 'oficina_normativa', 'sefin': 'secretaria_de_fin_HN.SIAFI2'}
    available_systems = {'HC1': 'honducompras-1', 'CE': 'catalogo-electronico', 'DDC': 'difusion-directa-contrato'}

    @classmethod
    def from_crawler(cls, crawler, publisher=None, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, publisher=publisher, system=system, *args, **kwargs)
        if publisher and spider.publisher not in spider.available_publishers:
            raise SpiderArgumentError(f'spider argument `publisher`: {spider.publisher!r} not recognized')

        if system:
            if spider.publisher != 'oncae':
                raise SpiderArgumentError(f'spider argument `system` is not supported for publisher: '
                                          f'{spider.publisher!r}')
            if spider.system not in spider.available_systems:
                raise SpiderArgumentError(f'spider argument `system`: {spider.system!r} not recognized')

        return spider

    def build_urls(self, date):
        for publisher in self.available_publishers:
            if self.publisher and publisher != self.publisher:
                continue

            if publisher == 'oncae':
                for system in self.available_systems:
                    if self.system and system != self.system:
                        continue
                    yield self.pattern.format(f"{self.available_publishers[publisher]}_"
                                              f"{self.available_systems[system]}_{date.year}_{date.month:02d}.json")
            else:
                yield self.pattern.format(f"{self.available_publishers[publisher]}_"
                                          f"{date.year}_{date.month:02d}.json")

    def get_formatter(self):
        return components(-1)
