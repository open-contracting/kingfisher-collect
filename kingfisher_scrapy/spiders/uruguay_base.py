import hashlib
from datetime import date, timedelta

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class UruguayBase(BaseSpider):
    base_url = 'http://comprasestatales.gub.uy/ocds/rss/{year:d}/{month:02d}'
    download_delay = 0.9

    def start_requests(self):
        current_date = date(2017, 11, 1)
        if self.sample:
            end_date = date(2017, 12, 1)
        else:
            end_date = date.today().replace(day=1)

        while current_date < end_date:
            current_date += timedelta(days=32)
            current_date.replace(day=1)

            url = self.base_url.format(year=current_date.year, month=current_date.month)
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                callback=self.parse_list
            )

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type=response.request.meta['data_type']
        )
