import json

from kingfisher_scrapy.base_spider import BaseSpider


# This Spider uses the old system of pipelines! DO NOT USE IT AS AN EXAMPLE OF WHAT TO DO IN FUTURE SPIDERS!
# Thank you.
class CanadaMontreal(BaseSpider):
    name = 'canada_montreal'
    start_urls = ['https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=1']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.OldKingfisherFilesPipeline': 400,
            'kingfisher_scrapy.pipelines.OldKingfisherPostPipeline': 800,
        }
    }

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        total = data['meta']['count']
        offset = 0
        limit = 10000
        if hasattr(self, 'sample') and self.sample == 'true':
            total = 1
            limit = 50
        while offset < total:
            yield {
                'file_urls': ['https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=%d&offset=%d' %
                              (limit, offset)],
                'data_type': 'release_package',
            }
            offset += limit
