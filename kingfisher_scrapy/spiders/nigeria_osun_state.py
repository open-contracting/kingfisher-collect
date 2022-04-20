import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, get_parameter_value, handle_http_error


class NigeriaOsunState(SimpleSpider):
    """
    Domain
      Nigeria Osun State Open Contracting Portal
    Bulk download documentation
      https://egp.osunstate.gov.ng/awarded_contracts.php
    """
    name = 'nigeria_osun_state'

    # SimpleSpider
    data_type = 'release_packageNew'

    # Local
    url_prefix = 'https://egp.osunstate.gov.ng/'

    def start_requests(self):
        url = f'{self.url_prefix}awarded_contracts.php'
        yield scrapy.Request(url, meta={'file_name': 'all.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath('//table[@id="contractTable"]/tbody/tr/td[2]/a/@href').getall():
            # The URLs look like
            # https://egp.osunstate.gov.ng/existing_award_details.php?id=ocds-xwwr9a-000103-OS/HLT/02
            ocid = get_parameter_value(url, 'id').replace('/', '_')
            yield self.build_request(f'{self.url_prefix}media/{ocid}.json', formatter=components(-1))
