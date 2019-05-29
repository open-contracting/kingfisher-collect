import csv
import scrapy

from datetime import date
from kingfisher_scrapy.spiders.paraguay_base import ParaguayDNCPBaseSpider


class ParaguayDNCPReleases(ParaguayDNCPBaseSpider):

    name = 'paraguay_dncp_releases'

    # For the releases, we have different CSVs, each of one have the process ids for the releases of each stage
    stages = {'planificaciones': 'planning', 'convocatorias': 'tender', 'adjudicaciones': 'award',
              'contratos': 'contract', 'modificacion_contrato': 'amendmment'}

    def start_requests(self):
        base_url = 'https://www.contrataciones.gov.py/images/opendata/{}/{:d}.csv'
        max_year = 2011 if self.is_sample() else date.today().year + 1
        for year in range(2010, max_year):
            for stage in list(self.stages.keys()):
                yield scrapy.Request(base_url.format(stage, year), meta={'meta': True, 'stage': stage, 'auth': False})

    def parse(self, response):
        if response.status == 200:
            base_url = 'https://www.contrataciones.gov.py:443/datos/api/v2/doc/ocds/{}/{}'
            if response.request.meta['meta']:

                # THe process id is in the column 0, and we discard the first row, that it is the title
                reader = csv.reader(response.text.splitlines(), delimiter=',')
                releases_ids = [row[0] for row in reader][1:] if not self.is_sample() \
                    else [row[0] for row in reader][1:10]

                stage = self.stages[response.request.meta['stage']]

                # The modificacion contrato CSV has the ids in the 3 row
                if stage == 'modificacion_contrato':
                    releases_ids = [row[2] for row in reader][1:] if not self.is_sample() \
                        else [row[2] for row in reader][1:10]

                for release_id in releases_ids:
                    yield scrapy.Request(
                        url=base_url.format(stage, release_id),
                        meta={'kf_filename': 'release{}-{}.json'.format(stage, release_id),
                              'meta': False},
                        dont_filter=True
                    )
            else:
                self.save_response_to_disk(response, response.request.meta['kf_filename'])
                yield {
                    'success': True,
                    'file_name': response.request.meta['kf_filename'],
                    'data_type': 'release_package',
                    'url': response.request.url,
                }
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
