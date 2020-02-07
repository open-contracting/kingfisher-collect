import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class IndonesiaBandung(BaseSpider):
    name = 'indonesia_bandung'

    base_url = 'https://webhooks.mongodb-stitch.com/api/client/v2.0/app/birms-cvrbm/service/query-birms' \
               '/incoming_webhook/find-releases?secret=6WkBFKh6SS4ibE2O0Fm5UHGEQWv8hQbj&limit=50'
    next_url = base_url + '&fromId={}'

    def start_requests(self):
        yield scrapy.Request(
            url=self.base_url,
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):

        if response.status == 200:
            json_data = json.loads(response.text)
            if len(json_data) == 0:
                return
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="release_list")

            if not self.is_sample():
                last_id = json_data[len(json_data)-1]['_id']
                yield scrapy.Request(
                    url=self.next_url.format(last_id),
                    meta={'kf_filename': 'page{}.json'.format(last_id)}
                )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
