import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class NigeriaAnambraState(SimpleSpider):
    """
    Domain
      Anambra State - Nigeria
    API documentation
      http://www.mepbdp.org.ng/ocds/api
    """
    name = 'nigeria_anambra_state_records'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://www.mepbdp.org.ng/ocds/api/mda_list',
            meta={'file_name': 'mda.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        mdas = response.json()
        for mda in mdas:
            url = 'http://www.mepbdp.org.ng/ocds/api/mda_records/{}'
            yield self.build_request(url.format(mda['id']), formatter=components(-2))
