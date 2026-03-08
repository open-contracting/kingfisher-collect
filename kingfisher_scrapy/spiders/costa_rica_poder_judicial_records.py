import datetime

from kingfisher_scrapy.base_spiders import CKANSpider, SimpleSpider
from kingfisher_scrapy.util import components


class CostaRicaPoderJudicialRecords(CKANSpider, SimpleSpider):
    """
    Domain
      Poder Judicial de Costa Rica
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2018'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://ckanpj.azurewebsites.net/dataset/estandar-de-datos-de-contrataciones-abiertas-ocds
    """

    name = "costa_rica_poder_judicial_records"

    # BaseSpider
    date_format = "year"
    default_from_date = "2018"
    skip_pluck = "Already covered (see code for details)"  # costa_rica_poder_judicial_releases

    # SimpleSpider
    data_type = "record_package"

    # CKANSpider
    ckan_api_url = "https://ckanpj.azurewebsites.net"
    ckan_package_id = "estandar-de-datos-de-contrataciones-abiertas-ocds"
    # e.g. https://ckanpj.azurewebsites.net/datosabiertos/OpenContracting/2018.json
    formatter = components(-1)

    # CKANSpider
    def get_resource_date(self, resource):
        return datetime.datetime(int(self.formatter(resource["url"])), 1, 1, tzinfo=datetime.timezone.utc)
