from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components


class HondurasPortalBulkFiles(PeriodicSpider):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      from_date
        Download only releases from this date onward (YYYY-MM format).
        If ``until_date`` is provided and ``from_date`` don't, defaults to '2005-11'.
      until_date
        Download only releases until this date (YYYY-MM format).
        If ``from_date`` is provided and ``until_date`` don't, defaults to current year-month.
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
    data_type = 'release_package'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    available_publishers = {'oncae': 'oficina_normativa', 'sefin': 'secretaria_de_fin_HN.SIAFI2'}
    oncae_systems = {'HC1': 'honducompras-1', 'CE': 'catalogo-electronico', 'DDC': 'difusion-directa-contrato'}

    # PeriodicSpider variables
    date_format = 'year-month'
    default_from_date = '2005-11'
    pattern = 'http://www.contratacionesabiertas.gob.hn/api/v1/descargas/{}'

    @classmethod
    def from_crawler(cls, crawler, publisher=None, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, publisher=publisher, system=system, *args, **kwargs)
        if publisher and spider.publisher not in spider.available_publishers:
            raise SpiderArgumentError(f'spider argument `publisher`: {spider.publisher!r} not recognized')

        if system:
            if spider.system not in spider.oncae_systems:
                raise SpiderArgumentError(f'spider argument `system`: {spider.system!r} not recognized')
            spider.publisher = 'oncae'

        return spider

    def build_urls(self, date):
        for publisher in self.available_publishers:
            if self.publisher and publisher != self.publisher:
                continue

            if publisher == 'oncae':
                for system in self.oncae_systems:
                    if self.system and system != self.system:
                        continue
                    yield self.pattern.format(f"{self.available_publishers.get(publisher)}_"
                                              f"{self.oncae_systems.get(system)}_{date.year}_{date.month:02d}.json")
            else:
                yield self.pattern.format(f"{self.available_publishers.get(publisher)}_"
                                          f"{date.year}_{date.month:02d}.json")

    def get_formatter(self):
        return components(-1)
