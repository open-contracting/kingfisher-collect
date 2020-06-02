from datetime import date

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Australia(LinksSpider):
    name = 'australia'
    data_type = 'release_package'
    next_page_formatter = parameters('cursor')

    def start_requests(self):
        url = f'https://api.tenders.gov.au/ocds/findByDates/contractPublished/' \
              f'2004-01-01T00:00:00Z/{date.today().year}-12-31T23:59:59Z'

        yield scrapy.Request(url, meta={'kf_filename': 'start.json'})
