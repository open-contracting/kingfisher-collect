import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class NigeriaEnuguState(SimpleSpider):
    """
    Domain
      Enugu State Open Contracting Portal
    Bulk download documentation
      https://dueprocess.en.gov.ng/ocds_report.php
    """

    name = 'nigeria_enugu_state'

    # BaseSpider
    validate_json = True  # https://github.com/open-contracting/kingfisher-collect/issues/963

    # SimpleSpider
    data_type = 'release_package'

    # Local
    url_prefix = 'https://dueprocess.en.gov.ng/'

    def start_requests(self):
        url = f'{self.url_prefix}ocds_report.php/'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        pattern = '//table[@id="contractTable"]/tbody/tr/td[3]/a/@href'
        for item in response.xpath(pattern).getall():
            yield self.build_request(f'{self.url_prefix}{item}', formatter=components(-1))
