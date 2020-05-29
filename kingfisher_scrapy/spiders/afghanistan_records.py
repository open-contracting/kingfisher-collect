import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class AfghanistanRecords(BaseSpider):
    """
    API documentation
      https://ocds.ageops.net/
    Spider arguments
      sample
        Download only 1 record.
    """
    name = 'afghanistan_records'
    download_delay = 1

    def start_requests(self):
        yield scrapy.Request(
            url='https://ocds.ageops.net/api/ocds/records',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        files_urls = json.loads(response.text)
        if self.sample:
            files_urls = [files_urls[0]]

        for file_url in files_urls:
            yield scrapy.Request(
                url=file_url,
                meta={'kf_filename': file_url.split('/')[-1] + '.json'},
                callback=self.parse_record
            )

    @handle_error
    def parse_record(self, response):
        yield self.build_file_from_response(response, response.request.meta['kf_filename'], data_type="record")
