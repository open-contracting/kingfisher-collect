import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, get_parameter_value, handle_http_error


class MoldovaPositiveInitiative(SimpleSpider):
    """
    Domain
      Positive Initiative
    Bulk download documentation
      https://www.tender.health/ocdsrelease
    """
    name = 'moldova_positive_initiative'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://www.tender.health/ocdsrelease'
        yield scrapy.Request(url, meta={'file_name': 'page.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        hrefs = response.xpath('//a/@href').getall()
        for href in hrefs:
            if '.json' in href:
                # the href looks like
                # http://www.google.com/url?q=http%3A%2F%2F116.202.173.47%3A8080%2Fmd_covid_2020-11-06.json&sa=D&sntz=1
                url = get_parameter_value(href, 'q')
                if not url:
                    url = href
                yield self.build_request(url, formatter=components(-1))
