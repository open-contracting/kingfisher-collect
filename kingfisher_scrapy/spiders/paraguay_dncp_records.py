import csv
from datetime import date

import scrapy

from kingfisher_scrapy.spiders.paraguay_base import ParaguayBase, AuthTokenRequest


class ParaguayDNCPRecords(ParaguayBase):

    name = 'paraguay_dncp_records'

    def start_requests(self):
        # First we download a CSV with all the ids to request for all the years
        self.request_token = self.settings.get('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN')
        if self.request_token is None:
            raise RuntimeError('No request token available')
        self.get_access_token(first=True)
        base_url = 'https://www.contrataciones.gov.py/images/opendata/planificaciones/{:d}.csv'
        max_year = 2011 if self.is_sample() else date.today().year + 1
        for year in range(2010, max_year):
            yield scrapy.Request(base_url.format(year), meta={'meta': True})

    def parse(self, response):
        if response.status == 200:
            base_url = 'https://www.contrataciones.gov.py:443/datos/api/v2/doc/ocds/record-package/{}'
            if response.request.meta['meta']:
                # THe process id is in the column 2, and we discard the first row, that it is the title
                reader = csv.reader(response.text.splitlines(), delimiter=',')
                record_ids = [row[2] for row in reader][1:] if not self.is_sample() \
                    else [row[2] for row in reader][1:10]
                for record_id in record_ids:
                    yield AuthTokenRequest(
                        url=base_url.format(record_id),
                        meta={'kf_filename': 'record{}.json'.format(record_id), 'meta': False},
                        dont_filter=True
                    )
            else:
                # We update the number of remaining request calling the get access token method
                self.get_access_token(response=response)
                self.save_response_to_disk(response, response.request.meta['kf_filename'])
                yield {
                    'success': True,
                    'file_name': response.request.meta['kf_filename'],
                    'data_type': 'record_package',
                    'url': response.request.url,
                }
        elif response.status == 401 or response.status == 429:
            yield AuthTokenRequest(
                url=response.request.url,
                meta=response.request.meta
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
