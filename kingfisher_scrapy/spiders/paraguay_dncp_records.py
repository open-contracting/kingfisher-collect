import csv
import scrapy

from datetime import date
from kingfisher_scrapy.spiders.paraguay_base import ParaguayDNCPBaseSpider


class ParaguayDNCPRecords(ParaguayDNCPBaseSpider):

    name = 'paraguay_dncp_records'

    def start_requests(self):
        base_url = 'https://www.contrataciones.gov.py/images/opendata/planificaciones/{:d}.csv'
        max_year = 2011 if self.is_sample() else date.today().year + 1
        for year in range(2010, max_year):
            yield scrapy.Request(base_url.format(year), meta={'meta': True, 'auth': False})

    def parse(self, response):
        if response.status == 200:
            base_url = 'https://www.contrataciones.gov.py:443/datos/api/v2/doc/ocds/record-package/{}'
            if response.request.meta['meta']:
                # THe process id is in the column 2, and we discard the first row, that it is the title
                reader = csv.reader(response.text.splitlines(), delimiter=',')
                record_ids = [row[2] for row in reader][1:] if not self.is_sample() \
                    else [row[2] for row in reader][1:10]
                for record_id in record_ids:
                    yield scrapy.Request(
                        url=base_url.format(record_id),
                        meta={'kf_filename': 'record{}.json'.format(record_id), 'meta': False},
                        dont_filter=True
                    )
            else:
                self.save_response_to_disk(response, response.request.meta['kf_filename'])
                yield {
                    'success': True,
                    'file_name': response.request.meta['kf_filename'],
                    'data_type': 'record_package',
                    'url': response.request.url,
                }
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
