import json
import scrapy
from kingfisher_scrapy.base_spider import BaseSpider


class HondurasPortalRecords(BaseSpider):
    name = 'honduras_portal_records'
    download_delay = 1.5
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='http://200.13.162.86/api/v1/record/?format=json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data['results']).encode(),
                response.request.meta['kf_filename'],
                data_type='record_list',
                url=response.request.url
            )

            url = json_data['next']
            if not url or self.is_sample():
                return
            else:
                yield scrapy.Request(
                    url,
                    meta={'kf_filename': 'page%s.json' % url[53:]}
                )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
