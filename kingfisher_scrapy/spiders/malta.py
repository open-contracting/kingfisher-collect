import datetime
from urllib.parse import urlsplit

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class Malta(CompressedFileSpider):
    """
    Domain
      Malta
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2019-10'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://docs.google.com/document/d/1VnCEywKkkQ7BcVbT7HlW2s_N_QI8W0KE/edit
    """
    name = 'malta'

    # SimpleSpider
    data_type = 'record_package'
    date_format = 'year-month'
    default_from_date = '2019-10'

    def start_requests(self):
        yield scrapy.Request(
            'http://demowww.etenders.gov.mt/ocds/services/recordpackage/getrecordpackagelist',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()['packagesPerMonth']
        netloc = urlsplit(response.request.url).netloc
        for url in reversed(urls):
            if self.from_date and self.until_date:
                # URL looks like:
                # http://malta-demo-server.eurodyn.com/ocds/services/recordpackage/getrecordpackage/2020/1
                year, month = map(int, url.rsplit('/', 2)[1:])
                url_date = datetime.datetime(year, month, 1)
                if not (self.from_date <= url_date <= self.until_date):
                    continue
            yield self.build_request(urlsplit(url)._replace(netloc=netloc).geturl(),
                                     formatter=join(components(-2), extension='zip'))
