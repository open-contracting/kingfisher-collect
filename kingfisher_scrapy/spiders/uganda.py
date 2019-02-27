import re
import json
import scrapy
from kingfisher_scrapy.base_spider import BaseSpider


# This Spider uses the old system of pipelines! DO NOT USE IT AS AN EXAMPLE OF WHAT TO DO IN FUTURE SPIDERS!
# Thank you.
class Uganda(BaseSpider):
    name = 'uganda'
    base_url = 'http://gpp.ppda.go.ug/api/v1/releases?tag={tag}&page={page}'
    tags = ['planning', 'tender', 'award', 'contract']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.OldKingfisherFilesPipeline': 400,
            'kingfisher_scrapy.pipelines.OldKingfisherPostPipeline': 800,
        }
    }

    def start_requests(self):
        tags = Uganda.tags
        if hasattr(self, 'sample') and self.sample == 'true':
            tags = [tags[0]]
        return [scrapy.Request(Uganda.base_url.format(tag=tag, page=1)) for tag in tags]

    def parse(self, response):
        data = json.loads(response.text)
        max_page = data['pagination']['last_page'] + 1
        tag = re.search(r'\?tag\=([a-z]+)', response.url).group(1)

        if hasattr(self, 'sample') and self.sample == 'true':
            max_page = 2

        for i in range(1, max_page):
            yield {
                'file_urls': [Uganda.base_url.format(tag=tag, page=i)],
                'data_type': 'release_package'
            }
