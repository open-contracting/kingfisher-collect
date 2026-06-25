from kingfisher_scrapy.base_spiders import CKANSpider, SimpleSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, MAX_DOWNLOAD_TIMEOUT, components


class ArgentinaBuenosAires(CKANSpider, SimpleSpider):
    """
    Domain
      Ciudad de Buenos Aires
    API documentation
      https://data.buenosaires.gob.ar/acerca/ckan
    Bulk download documentation
      https://data.buenosaires.gob.ar/dataset/buenos-aires-compras
    """

    name = "argentina_buenos_aires"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": MAX_DOWNLOAD_TIMEOUT,
        "USER_AGENT": BROWSER_USER_AGENT,
    }

    # BaseSpider
    unflatten = True
    unflatten_combine = True

    # SimpleSpider
    data_type = "release_package"

    # CKANSpider
    ckan_api_url = "https://data.buenosaires.gob.ar"
    ckan_package_id = "buenos-aires-compras"
    ckan_resource_format = "CSV"
    formatter = staticmethod(components(-1))

    def parse_list(self, response):
        requests = list(super().parse_list(response))
        # Filter bac_anual.csv and bac.csv as they are covered by other files
        self.csv_total = len(requests) - 2
        for request in requests:
            if components(-1)(request.url) in ("bac_anual.csv", "bac.csv"):
                continue
            else:
                yield request
