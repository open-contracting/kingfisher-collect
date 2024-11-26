import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT


class CanadaMontreal(IndexSpider):
    """
    Domain
      Ville de Montréal
    API documentation
      http://donnees.ville.montreal.qc.ca/dataset/contrats-et-subventions-api
    """

    name = 'canada_montreal'
    # Publisher uses Cloudflare (CF-Cache-Status and CF-RAY response headers, can verify with curl).
    # Cloudflare responds with HTTP 520 if request headers use default user agent.
    user_agent = BROWSER_USER_AGENT

    # BaseSpider
    ocds_version = '1.0'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    result_count_pointer = '/meta/count'
    limit = 10000  # > 10000 causes "Too many records requested. Set parameter LIMIT lower"

    def start_requests(self):
        url = f'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit={self.limit}'
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'}, callback=self.parse_list)
