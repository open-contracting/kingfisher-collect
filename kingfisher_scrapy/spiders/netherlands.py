import datetime

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class Netherlands(SimpleSpider):
    """
    Domain
      TenderNed
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2016'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://www.tenderned.nl/cms/nl/aanbesteden-in-cijfers/datasets-aanbestedingen
    """

    name = 'netherlands'
    download_timeout = 99999  # to avoid user timeout when downloading the file

    # SimpleSpider
    data_type = 'release_package'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2016'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.tenderned.nl/cms/nl/aanbesteden-in-cijfers/datasets-aanbestedingen',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath('//article/div/ul/li/a/@href').getall():
            if url.endswith('.json'):
                if self.from_date and self.until_date:
                    # URL looks like https://www.tenderned.nl/cms/sites/default/files/2023-04/2017.json
                    year = int(url.rsplit('/', 1)[1].replace('.json', ''))
                    url_date = datetime.datetime(year, 1, 1)
                    if not (self.from_date <= url_date <= self.until_date):
                        continue
                yield self.build_request(url, formatter=components(-1))
