import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, components, get_parameter_value


class NigeriaOsunState(SimpleSpider):
    """
    Domain
      Nigeria Osun State Open Contracting Portal
    Bulk download documentation
      https://egp.osunstate.gov.ng/awarded_contracts.php#
    """
    name = 'nigeria_osun_state'
    base_url = 'https://egp.osunstate.gov.ng/'

    # SimpleSpider
    data_type = 'release_packageNew'

    def start_requests(self):
        url = f'{self.base_url}awarded_contracts.php'
        yield scrapy.Request(url, meta={'file_name': 'all.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        pattern = '//table[@id="contractTable"]/tbody/tr/td[2]/a/@href'
        for item in response.xpath(pattern):
            # The URL looks like https://egp.osunstate.gov.ng/existing_award_details.php?id=ocds-xwwr9a-000103-OS/HLT/02
            ocid = get_parameter_value(item.get(), 'id').replace('/', '_')
            yield self.build_request(f'{self.base_url}media/{ocid}.json', formatter=components(-1))
