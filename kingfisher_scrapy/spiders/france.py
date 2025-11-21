import scrapy

from kingfisher_scrapy.base_spiders import BigFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class France(BigFileSpider):
    """
    Domain
      Ministère de l'Économie, des Finances et de l'Industrie
    Swagger API documentation
      https://doc.data.gouv.fr/api/reference/
    """

    name = "france"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        # A CKAN API JSON response.
        # Ministère de l'économie, des finances et de la relance
        # https://www.data.gouv.fr/fr/datasets/donnees-essentielles-de-la-commande-publique-fichiers-consolides/
        yield scrapy.Request(
            "https://www.data.gouv.fr/api/1/datasets/donnees-essentielles-de-la-commande-publique-fichiers-consolides/",
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()["resources"]:
            description = resource["description"]
            if description and "ocds" in description.lower():
                yield self.build_request(resource["url"], formatter=components(-2))
