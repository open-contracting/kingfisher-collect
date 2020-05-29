import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class AustraliaNSW(BaseSpider):
    name = 'australia_nsw'

    def start_requests(self):
        release_types = ['planning', 'tender', 'contract']
        page_limit = 10 if self.sample else 1000
        url = 'https://tenders.nsw.gov.au/?event=public.api.{}.search&ResultsPerPage={}'
        for release_type in release_types:
            yield scrapy.Request(
                url.format(release_type, page_limit),
                meta={
                    'kf_filename': '{}.json'.format(release_type),
                    'release_type': release_type,
                },
                callback=self.parse_list
            )

    def parse_list(self, response):
        if self.is_http_success(response):

            json_data = json.loads(response.text)
            release_type = response.request.meta['release_type']

            # More Pages?
            if 'links' in json_data and isinstance(json_data['links'], dict) and 'next' in json_data['links'] \
                    and not self.sample:
                yield scrapy.Request(
                    json_data['links']['next'],
                    meta={
                        'kf_filename': hashlib.md5(json_data['links']['next'].encode('utf-8')).hexdigest() + '.json',
                        'release_type': release_type,
                    },
                    callback=self.parse_list
                )

            # Data?
            for release in json_data['releases']:
                if release_type == 'planning':
                    uuid = release['tender']['plannedProcurementUUID']
                    yield scrapy.Request(
                        'https://tenders.nsw.gov.au/?event=public.api.planning.view&PlannedProcurementUUID=%s' % uuid,
                        meta={'kf_filename': 'plannning-%s.json' % uuid},
                        callback=self.parse
                    )
                if release_type == 'tender':
                    uuid = release['tender']['RFTUUID']
                    yield scrapy.Request(
                        'https://tenders.nsw.gov.au/?event=public.api.tender.view&RFTUUID=%s' % uuid,
                        meta={'kf_filename': 'tender-%s.json' % uuid},
                        callback=self.parse
                    )
                if release_type == 'contract':
                    for award in release['awards']:
                        uuid = award['CNUUID']
                        yield scrapy.Request(
                            'https://tenders.nsw.gov.au/?event=public.api.contract.view&CNUUID=%s' % uuid,
                            meta={'kf_filename': 'contract-%s.json' % uuid},
                            callback=self.parse
                        )

        else:
            yield self.build_file_error_from_response(
                response, file_name=hashlib.md5(response.request.url.encode('utf-8')).hexdigest() + '.json')

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                            data_type='release_package')
