from kingfisher_scrapy.base_spiders import CKANSpider, CompressedFileSpider
from kingfisher_scrapy.util import components


class CostaRicaPoderJudicialReleases(CKANSpider, CompressedFileSpider):
    """
    Domain
      Poder Judicial de Costa Rica
    Bulk download documentation
      https://ckanpj.azurewebsites.net/dataset/estandar-de-datos-de-contrataciones-abiertas-ocds
    """

    name = "costa_rica_poder_judicial_releases"

    # BaseSpider
    validate_json = True  # https://github.com/open-contracting/kingfisher-collect/issues/876

    # SimpleSpider
    data_type = "release_package"

    # CompressedFileSpider
    # The ZIP file contains release packages and record packages. The filenames of release packages contain "-".
    file_name_must_contain = "-"

    # CKANSpider
    ckan_api_url = "https://ckanpj.azurewebsites.net"
    ckan_package_id = "estandar-de-datos-de-contrataciones-abiertas-ocds"
    ckan_resource_format = "ZIP"
    # https://pjcrdatosabiertos.blob.core.windows.net/datosabiertos/OpenContracting/ocds-fnha3a-FULL.zip
    formatter = components(-1)
