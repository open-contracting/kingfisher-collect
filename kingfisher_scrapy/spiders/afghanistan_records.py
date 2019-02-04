import json

from kingfisher_scrapy.base_spider import BaseSpider


class AfghanistanRecords(BaseSpider):
    name = 'afghanistan_records'
    start_urls = ['https://ocds.ageops.net/api/ocds/records']
    download_delay = 1

    def parse(self, response):
        files_urls = json.loads(response.body)
        if hasattr(self, 'sample') and self.sample == 'true':
            files_urls = [files_urls[0]]

        for file_url in files_urls:
            yield {
                'file_urls': [file_url],
                'data_type': 'record'
            }
