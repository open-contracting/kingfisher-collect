import re
from datetime import date
from datetime import timedelta

from kingfisher_scrapy.base_spider import BaseXMLFeedSpider


class Uruguay(BaseXMLFeedSpider):
    name = 'uruguay'
    intertag = 'item'
    base_url = 'http://comprasestatales.gub.uy/ocds/rss/{year:d}/{month:02d}'
    download_delay = 0.9
    randomize_download_delay = False

    def start_requests(self):
        current_date = date(2017, 11, 1)  # feed starts in 2017/12

        if hasattr(self, 'sample') and self.sample == 'true':
            end_date = date(2017, 12, 1)
        else:
            end_date = date.today().replace(day=1)

        while current_date < end_date:
            current_date += timedelta(days=32)
            current_date.replace(day=1)

            url = Uruguay.base_url.format(year=current_date.year, month=current_date.month)
            yield self.make_requests_from_url(url)

    def adapt_response(self, response):
        if hasattr(self, 'sample') and self.sample == 'true':
            parts = re.split('\<item\>', response.text) # noqa
            new_response = response.replace(body=parts[0] + '<item>' + parts[-1])
            return new_response
        return response

    def parse_node(self, response, node):
        yield {
            'file_urls': node.xpath('link/text()').extract(),
            'data_type': 'release_package'
        }
