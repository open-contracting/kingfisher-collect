import csv
from datetime import date

import requests
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ParaguayDNCPReleases(BaseSpider):
    REQUEST_TOKEN = 'Basic ' \
                    'ODhjYmYwOGEtMDcyMC00OGY1LWFhYWUtMWVkNzVkZmFiYzZiOjNjNjQxZGQ5LWNjN2UtNDI5ZC05NWRiLWI5ODNiNmYy' \
                    'MDY3NA== '
    name = 'paraguay_dncp_releases'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }
    access_token = ''

    def start_requests(self):
        self.get_access_token()
        base_url = 'https://www.contrataciones.gov.py/images/opendata/{}/{:d}.csv'
        max_year = 2011 if self.is_sample() else date.today().year + 1
        for year in range(2010, max_year):
            for stage in ['planificaciones', 'convocatorias', 'adjudicaciones', 'contratos', 'modificacion_contrato']:
                yield scrapy.Request(base_url.format(stage, year), meta={'meta': True, 'stage': stage})

    def parse(self, response):
        if response.status == 200:
            base_url = 'https://www.contrataciones.gov.py:443/datos/api/v2/doc/ocds/{}/{}'
            if response.request.meta['meta']:
                reader = csv.reader(response.text.splitlines(), delimiter=',')
                releases_ids = [row[0] for row in reader][1:] if not self.is_sample() \
                    else [row[0] for row in reader][1:10]
                stage = ''
                if response.request.meta['stage'] == 'planificaciones':
                    stage = 'planning'
                elif response.request.meta['stage'] == 'convocatorias':
                    stage = 'tender'
                elif response.request.meta['stage'] == 'adjudicaciones':
                    stage = 'award'
                elif response.request.meta['stage'] == 'contratos':
                    stage = 'contract'
                elif response.request.meta['stage'] == 'modificacion_contrato':
                    stage = 'amendmment'

                for release_id in releases_ids:
                    yield scrapy.Request(
                        url=base_url.format(stage, release_id),
                        meta={'kf_filename': 'release{}-{}.json'.format(stage, release_id),
                              'meta': False},
                        headers={'Authorization': self.access_token}
                    )
            else:
                self.save_response_to_disk(response, response.request.meta['kf_filename'])
                yield {
                    'success': True,
                    'file_name': response.request.meta['kf_filename'],
                    'data_type': 'release_package',
                    'url': response.request.url,
                }
        elif response.status == 403:
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
            data_json = ''
            while not correct:
                r = requests.post('https://www.contrataciones.gov.py:443/datos/api/oauth/token',
                                  headers={'Authorization': self.REQUEST_TOKEN})
                try:
                    data_json = r.json()['access_token']
                    correct = True
                except requests.exceptions.RequestException:
                    correct = False
            self.access_token = 'Bearer ' + data_json
            return self.access_token
