import datetime

from kingfisher_scrapy.base_spiders import CKANSpider, SimpleSpider
from kingfisher_scrapy.util import components


class CanadaQuebec(CKANSpider, SimpleSpider):
    """
    Domain
      Secrétariat du Conseil du trésor
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2021-03-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Bulk download documentation
      https://www.donneesquebec.ca/recherche/dataset/systeme-electronique-dappel-doffres-seao
    """

    name = "canada_quebec"

    # BaseSpider
    default_from_date = "2021-03-01"

    # SimpleSpider
    data_type = "release_package"

    # CKANSpider
    ckan_api_url = "https://www.donneesquebec.ca"
    ckan_package_id = "d23b2e02-085d-43e5-9e6e-e1d558ebfdd5"
    # The same filename can be generated on different dates, but containing different releases, like:
    # https://www.donneesquebec.ca/recherche/dataset/d23b2e02-085d-43e5-9e6e-e1d558ebfdd5/resource/c6f8d624-b4e7-4a82-bae3-ca78f01bc017/download/hebdo_20251222_20251228.json
    # https://www.donneesquebec.ca/recherche/dataset/d23b2e02-085d-43e5-9e6e-e1d558ebfdd5/resource/552da290-239f-4512-8f5d-4e0329e5d72d/download/hebdo_20251222_20251228.json
    formatter = components(-3)

    # CKANSpider
    def get_resource_date(self, resource):
        # Basename is like "hebdo_20210401_20210411" or "mensuel_20210301_20210331".
        return datetime.datetime.strptime(resource["url"].split("_")[-2], "%Y%m%d").replace(
            tzinfo=datetime.timezone.utc
        )
