import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class MexicoINAIPortal(SimpleSpider):
    """
    Spider arguments
      sample
        Downloads one page of records.
    """
    name = 'mexico_inai_portal'
    data_type = 'record'

    def build_url(self, page):
        return scrapy.FormRequest(
            'http://contratacionesabiertas.inai.org.mx/contratacionesabiertas/pagination',
            meta={'file_name': f'{page}.html'},
            callback=self.parse_list,
            formdata={'npage': page,
                      'keyword': '',
                      'process': '',
                      'stage': '',
                      'status': '',
                      'year': '',
                      'orderby': 'datesigned'}
        )

    def start_requests(self):
        yield self.build_url('1')

    @handle_http_error
    def parse_list(self, response):
        for row in response.xpath('//div[@class="contract-download col-md-1"]'):
            url = row.xpath('div/a/@href').extract_first()
            yield self.build_request(url, formatter=components(-1))
        next_page = response.xpath('//ul[@class="pagination"]/li/a[@aria-label="Next"]/@data-page').extract_first()
        if next_page and not self.sample:
            yield self.build_url(next_page)
