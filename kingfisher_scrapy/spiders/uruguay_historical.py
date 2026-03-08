import datetime

from kingfisher_scrapy.base_spiders import CKANSpider, CompressedFileSpider
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT, components


class UruguayHistorical(CKANSpider, CompressedFileSpider):
    """
    Domain
      Agencia Reguladora de Compras Estatales (ARCE)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2002'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    """

    name = "uruguay_historical"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": MAX_DOWNLOAD_TIMEOUT / 2,  # 15min
    }

    # BaseSpider
    date_format = "year"
    default_from_date = "2002"
    skip_pluck = "Already covered (see code for details)"  # uruguay_releases

    # SimpleSpider
    data_type = "release_package"

    # CKANSpider
    ckan_api_url = "https://catalogodatos.gub.uy"
    ckan_package_id = "arce-datos-historicos-de-compras"
    # e.g. https://catalogodatos.gub.uy/dataset/44d3-b09c/resource/1e39-453d/download/ocds-2002.zip
    formatter = components(-1)

    # CKANSpider
    def get_resource_date(self, resource):
        return datetime.datetime(int(self.formatter(resource["url"])[5:9]), 1, 1, tzinfo=datetime.timezone.utc)
