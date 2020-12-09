import scrapy
from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, get_parameter_value, handle_http_error


class MoldovaPositiveInitiative(SimpleSpider):
    """
       Domain
         Positive Initiative - Moldova
    Bulk download documentation
      https://www.tender.health/ocdsrelease
    """
    name = 'moldova_positive_initiative'
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://www.tender.health/ocdsrelease'
        yield scrapy.Request(url, meta={'file_name': 'page.html'}, callback=self.scrape_page)

    @handle_http_error
    def scrape_page(self, response, **kwargs):
        hrefs = response.xpath('//a/@href').getall()
        for href in hrefs:
            if '.json' in href:
                url = get_parameter_value(href, 'q')
                yield self.build_request(url, formatter=components(-1))
