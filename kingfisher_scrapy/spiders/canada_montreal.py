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
    data_type = 'release_package'
    limit = 10000
    ocds_version = '1.0'
    count_pointer = '/meta/count'
    formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        url = f'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit={self.limit}'
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'}, callback=self.parse_list)
