import scrapy
from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, get_parameter_value


class MoldovaPositiveInitiative(SimpleSpider):
    """
       Domain
         Positive Initiative - Moldova
    """
    name = 'moldova_positive_initiative'
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://www.tender.health/ocdsrelease'
        yield scrapy.Request(url, meta={'file_name': 'page.html'}, callback=self.scrape_page)

    def scrape_page(self, response, **kwargs):
        for href in response.xpath('//a/@href').getall():
            if '.json' in href:
                url = get_parameter_value(href, 'q')
                yield self.build_request(url, formatter=components(-1))
