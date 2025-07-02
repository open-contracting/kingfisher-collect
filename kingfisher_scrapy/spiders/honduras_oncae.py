from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT, components


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
      https://oncae.gob.hn/datos-abiertos/
    """

    name = "honduras_oncae"
    download_timeout = MAX_DOWNLOAD_TIMEOUT / 2  # 15min

    # BaseSpider
    date_format = "year"
    default_from_date = "2005"
    skip_pluck = "Already covered (see code for details)"  # honduras_portal_api_releases

    # SimpleSpider
    data_type = "release_package"

    # CompressedFileSpider
    yield_non_archive_file = True

    # PeriodicSpider
    pattern = "https://datosabiertos.oncae.gob.hn/datosabiertos/{}"
    formatter = staticmethod(components(-1))  # year

    # Local
    available_systems = {"HC1": 2005, "CE": 2014, "DDC": 2010}

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, system=system, **kwargs)
        if system and spider.system not in spider.available_systems:
            raise SpiderArgumentError(f"spider argument `system`: {spider.system!r} not recognized")
        return spider

    def build_urls(self, date):
        systems = self.available_systems
        for system in systems:
            if self.system and system != self.system:
                continue
            if date < systems[system] or (system == "DDC" and date > 2019):
                continue

            suffix = f"{date}.json" if system == "HC1" else f"{date}_json.zip"
            yield self.pattern.format(f"{system}/{system}_datos_{suffix}")
