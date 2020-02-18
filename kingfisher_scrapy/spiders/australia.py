import datetime
import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Australia(BaseSpider):

    name = 'australia'

    def start_requests(self):

        if self.sample:
            yield scrapy.Request(
                url='https://api.tenders.gov.au/ocds/findByDates/contractPublished/2018-01-01T00:00:00Z/2018-12-31T23'
                    ':59:59Z',
                meta={'kf_filename': 'year-2018.json'}
            )
        else:
            current_year = datetime.datetime.now().year + 1
            for year in range(2004, current_year):
                yield scrapy.Request(
                    url='https://api.tenders.gov.au/ocds/findByDates/contractPublished/'
                        '{}-01-01T00:00:00Z/{}-12-31T23:59:59Z'.format(year, year),
                    meta={'kf_filename': 'year-{}.json'.format(year)}
                )

    def parse(self, response):

        if response.status == 200:

            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type='release_package')

            json_data = json.loads(response.text)
            if not self.sampl
                if 'links' in json_data and 'next' in json_data['links'] and json_data['links']['next']:
                    yield scrapy.Request(
                        url=json_data['links']['next'],
                        meta={'kf_filename': 'page-%s.json' % hashlib.md5(
                            json_data['links']['next'].encode('utf-8')).hexdigest()}
                    )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
