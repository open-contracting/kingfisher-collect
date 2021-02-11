import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class IndiaCivicDataLab(SimpleSpider):
    """
    Domain
      Civic Data Lab India
    Bulk download documentation
      https://github.com/CivicDataLab/himachal-pradesh-health-procurement-OCDS/
    """
    name = 'india_civic_data_lab'

    # BaseSpider
    unflatten = True
    unflatten_args = {
        'metatab_name': 'Meta',
        'metatab_vertical_orientation': True
    }

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://github.com/CivicDataLab/himachal-pradesh-health-procurement-OCDS'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for path in response.xpath('//div[@role="rowheader"]/span/a/@href').getall():
            if path.endswith('.xlsx'):
                yield self.build_request(
                    f'https://github.com{path}?raw=true',
                    formatter=components(-1)
                )
