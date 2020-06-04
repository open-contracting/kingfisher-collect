import datetime
import hashlib

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class NepalPortal(BaseSpider):
    """
    Bulk download documentation
      http://ppip.gov.np/downloads
    Spider arguments
      sample
        Download only data released on 2018.
    """
    name = 'nepal_portal'

    def start_requests(self):
        if self.sample:
            current_year = 2018
            end_year = 2018
        else:
            current_year = 2013
            now = datetime.datetime.now()
            end_year = now.year

        while current_year <= end_year:
            url = 'http://ppip.gov.np/bulk-download/{}'.format(current_year)
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )
            current_year += 1

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type='release_package'
        )
