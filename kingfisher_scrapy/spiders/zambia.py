import json
from kingfisher_scrapy.base_spider import BaseSpider


# This Spider uses the old system of pipelines! DO NOT USE IT AS AN EXAMPLE OF WHAT TO DO IN FUTURE SPIDERS!
# Thank you.
class Zambia(BaseSpider):
    ext = '.zip'
    name = 'zambia'
    start_urls = ['https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.OldKingfisherFilesPipeline': 400,
            'kingfisher_scrapy.pipelines.OldKingfisherPostPipeline': 800,
        }
    }

    def parse(self, response):
        files_urls = json.loads(response.body)['packagesPerMonth']

        if hasattr(self, 'sample') and self.sample == 'true':
            files_urls = [files_urls[0]]

        for file_url in files_urls:
            yield {
                'file_urls': [file_url],
                'data_type': 'record_package'
            }
