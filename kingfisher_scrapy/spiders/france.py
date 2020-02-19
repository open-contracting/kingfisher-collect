import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class France(BaseSpider):
    name = "france"

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.data.gouv.fr/api/1/datasets/?organization=534fff75a3a7292c64a77de4',
            callback=self.parse_item
        )

    def parse_item(self, response):
        if response.status == 200:
            json_data = json.loads(response.text)
            data = json_data.get('data')
            for item in data:
                resources = item.get('resources')
                for resource in resources:
                    description = resource.get('description')
                    if description and (description.count("OCDS") or description.count("ocds")):
                        url = resource.get('url')
                        yield scrapy.Request(
                            url,
                            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                        )
                        if self.sample:
                            break
                else:
                    continue
                break
            else:
                next_page = json_data.get('next_page')
                if next_page:
                    yield scrapy.Request(
                        next_page,
                        callback=self.parse_item
                    )
        else:
            yield {
                'success': False,
                'url': response.request.url,
                'errors': {"http_code": response.status}
            }

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type="release_package"
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {"http_code": response.status}
            }
