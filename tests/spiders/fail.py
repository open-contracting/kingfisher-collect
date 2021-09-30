"""
This spider deliberately generates HTTP errors. You can use this to test whether errors are recorded properly.
"""
import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class Fail(SimpleSpider):
    name = 'fail'

    # BaseSpider
    skip_pluck = 'Not a real spider'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # Fine
        yield scrapy.Request(
            'https://raw.githubusercontent.com/open-contracting/sample-data/main/fictional-example/1.1/ocds-213czf-000-00001-01-planning.json',  # noqa: E501
            meta={'file_name': 'fine.json'}
        )
        # A straight 404
        yield scrapy.Request(
            'https://www.open-contracting.org/i-want-a-kitten',
            meta={'file_name': 'http-404.json'}
        )
        # I broke the server ....
        yield scrapy.Request('http://httpstat.us/500', meta={'file_name': 'http-500.json'})
        # .... but actually, yes, I also broke the Proxy too
        yield scrapy.Request('http://httpstat.us/502', meta={'file_name': 'http-502.json'})
