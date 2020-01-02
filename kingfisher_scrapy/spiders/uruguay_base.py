import hashlib
import json
from datetime import date
from datetime import timedelta

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class UruguayBase(BaseSpider):
    base_url = 'http://comprasestatales.gub.uy/ocds/rss/{year:d}/{month:02d}'
    download_delay = 0.9
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        current_date = date(2017, 11, 1)
        if self.is_sample():
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

    def parse(self, response):
        if response.status == 200:
            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type=response.request.meta['data_type'],
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
