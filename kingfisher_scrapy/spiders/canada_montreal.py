import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class CanadaMontreal(IndexSpider):
    """
    API documentation
      http://donnees.ville.montreal.qc.ca/dataset/contrats-et-subventions-api
    Spider arguments
      sample
        Downloads the first page of releases returned by the main endpoint.
    """
    name = 'canada_montreal'
    data_type = 'release_package'
    limit = 10000
    ocds_version = '1.0'
    count_pointer = '/meta/count'
    formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        url = 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit={step}'.format(step=self.limit)
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'}, callback=self.parse_list)
