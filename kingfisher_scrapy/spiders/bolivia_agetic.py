import scrapy

from kingfisher_scrapy.base_spider import FlattenSpider
from kingfisher_scrapy.util import components, handle_http_error


class BoliviaAgetic(FlattenSpider):
    """
    Bulk download documentation
      https://datos.gob.bo/id/dataset/contrataciones-agetic-2019-estandar-ocp
    Spider arguments
      sample
        Downloads the first file in the downloads page.
    """
    name = 'bolivia_agetic'
    data_type = 'release_list'

    def start_requests(self):
        url = 'https://datos.gob.bo/id/dataset/contrataciones-agetic-2019-estandar-ocp'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        html_urls = response.xpath('//li[@class="resource-item"]//a/@href').getall()
        for html_url in html_urls:
            if 'ocds' in html_url:
                yield self.build_request(html_url, formatter=components(-1))

            if self.sample:
                break
