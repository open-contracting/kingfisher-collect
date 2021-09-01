import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class CanadaMontreal(IndexSpider):
    """
    Domain
      Montréal, Québec
    API documentation
      http://donnees.ville.montreal.qc.ca/dataset/contrats-et-subventions-api
    """
    name = 'canada_montreal'

    # BaseSpider
    ocds_version = '1.0'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    count_pointer = '/meta/count'
    limit = 10000  # > 10000 causes "Too many records requested. Set parameter LIMIT lower"

    def start_requests(self):
        url = f'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit={self.limit}'
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'}, callback=self.parse_list)
