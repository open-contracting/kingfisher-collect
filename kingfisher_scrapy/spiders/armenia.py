import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Armenia(BaseSpider):
    """
    Spider arguments
      sample
        Download only the first release package in the dataset.
    """
    name = 'armenia'
    start_urls = ['https://armeps.am/ocds/release']

    def start_requests(self):
        yield scrapy.Request(
            url='https://armeps.am/ocds/release',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            yield self.save_response_to_disk(response, response.request.meta['kf_filename'],
                                             data_type='release_package')

            json_data = json.loads(response.text)
            if not self.sample:
                if 'next_page' in json_data and 'uri' in json_data['next_page']:
                    url = json_data['next_page']['uri']
                    yield scrapy.Request(
                        url=url,
                        meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest()+'.json'}
                    )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
