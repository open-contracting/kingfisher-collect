from datetime import date

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Australia(LinksSpider):
    """
    API documentation
      https://data.gov.au/dataset/ds-dga-5c7fa69b-b0e9-4553-b8df-2a022dd2e982/distribution/dist-dga-a7f471ad-e085-49b5-bd6b-1b270ea46e99/details?q=
    Swagger API documentation
      https://app.swaggerhub.com/apis/austender/ocds-api/1.1#/
    Spider arguments
      sample
        Download only data released on 2018.
    """
    name = 'australia'
    data_type = 'release_package'
    next_page_formatter = staticmethod(parameters('cursor'))

    def start_requests(self):
        url = f'https://api.tenders.gov.au/ocds/findByDates/contractPublished/' \
              f'2004-01-01T00:00:00Z/{date.today().year}-12-31T23:59:59Z'

        yield scrapy.Request(url, meta={'file_name': 'start.json'})
