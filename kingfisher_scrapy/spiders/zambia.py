import json
from kingfisher_scrapy.base_spider import BaseSpider


class Zambia(BaseSpider):
    ext = '.zip'
    name = 'zambia'
    start_urls = ['https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist']

    def parse(self, response):
        files_urls = json.loads(response.body)['packagesPerMonth']

        if hasattr(self, 'sample') and self.sample == 'true':
            files_urls = [files_urls[0]]

        for file_url in files_urls:
            yield {
                'file_urls': [file_url],
                'data_type': 'record_package'
            }
