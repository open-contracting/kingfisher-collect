import csv
from datetime import date

import requests
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ParaguayDNCPRecords(BaseSpider):
    REQUEST_TOKEN = 'Basic ' \
                    'ODhjYmYwOGEtMDcyMC00OGY1LWFhYWUtMWVkNzVkZmFiYzZiOjNjNjQxZGQ5LWNjN2UtNDI5ZC05NWRiLWI5ODNiNmYy' \
                    'MDY3NA== '
    name = 'paraguay_dncp_records'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }
    access_token = ''

    def start_requests(self):
        self.get_access_token()
        base_url = 'https://www.contrataciones.gov.py/images/opendata/planificaciones/{:d}.csv'
        max_year = 2011 if self.is_sample() else date.today().year + 1
        for year in range(2010, max_year):
            yield scrapy.Request(base_url.format(year), meta={'meta': True})

    def parse(self, response):
        if response.status == 200:
            base_url = 'https://www.contrataciones.gov.py:443/datos/api/v2/doc/ocds/record-package/{}'
            if response.request.meta['meta']:
                reader = csv.reader(response.text.splitlines(), delimiter=',')
                record_ids = [row[2] for row in reader][1:] if not self.is_sample() \
                    else [row[2] for row in reader][1:10]
                for record_id in record_ids:
                    yield scrapy.Request(
                        url=base_url.format(record_id),
                        meta={'kf_filename': 'record{}.json'.format(record_id), 'meta': False},
                        headers={'Authorization': self.access_token}
                    )
            else:
                self.save_response_to_disk(response, response.request.meta['kf_filename'])
                yield {
                    'success': True,
                    'file_name': response.request.meta['kf_filename'],
                    'data_type': 'record_package',
                    'url': response.request.url,
                }
        elif response.status == 401 or response.status == 429:
            self.access_token = self.get_access_token()
            yield scrapy.Request(
                url=response.request.url,
                meta={'kf_filename': response.request.meta['kf_filename'], 'meta': False},
                headers={'Authorization': self.get_access_token()}
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def get_access_token(self):
        if self.access_token:
            return 'Bearer ' + self.access_token
        else:
            correct = False
            json = ''
            while not correct:
                r = requests.post('https://www.contrataciones.gov.py:443/datos/api/oauth/token',
                                  headers={'Authorization': self.REQUEST_TOKEN})
                try:
                    json = r.json()['access_token']
                    correct = True
                except requests.exceptions.RequestException:
                    correct = False
            self.access_token = 'Bearer ' + json
            return self.access_token
