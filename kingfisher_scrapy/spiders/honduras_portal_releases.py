import json
import scrapy
from kingfisher_scrapy.base_spider import BaseSpider


class HondurasPortalReleases(BaseSpider):
    name = 'honduras_portal_releases'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            'http://200.13.162.86/api/v1/release/?format=json',
        )

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())
            file_url = json_data['next']

            yield scrapy.Request(file_url)

            file_name = response.request.url

            yield self.save_data_to_disk(json.dumps(json_data['results']).encode(), "page_" + file_name[54:] + ".json", data_type='release_list', url=response.request.url)

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['releases.json'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
