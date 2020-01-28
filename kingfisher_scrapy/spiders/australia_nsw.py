import json
import scrapy
import hashlib

from kingfisher_scrapy.base_spider import BaseSpider


class AustraliaNSW(BaseSpider):
    name = 'australia_nsw'
    start_urls = ['https://tenders.nsw.gov.au']
    custom_settings = {
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        release_types = ['planning', 'tender', 'contract']
        page_limit = 10 if self.is_sample() else 1000
        url = 'https://tenders.nsw.gov.au/?event=public.api.{}.search&ResultsPerPage={}'
        for release_type in release_types:
            yield scrapy.Request(
                url.format(release_type, page_limit),
                meta={'release_type': release_type},
                callback=self.parse_list
            )

    def parse_list(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())

            # More Pages?
            if 'links' in json_data and isinstance(json_data['links'], dict) and 'next' in json_data['links'] \
                    and not self.is_sample():
                yield scrapy.Request(
                    json_data['links']['next'],
                    meta={'release_type': response.request.meta['release_type']},
                    callback=self.parse_list
                )

            # Data?
            for release in json_data['releases']:
                if response.request.meta['release_type'] == 'planning':
                    uuid = release['tender']['plannedProcurementUUID']
                    yield scrapy.Request(
                        'https://tenders.nsw.gov.au/?event=public.api.planning.view&PlannedProcurementUUID=%s' % uuid,
                        meta={'kf_filename': 'plannning-%s.json' % uuid},
                        callback=self.parse
                    )
                if response.request.meta['release_type'] == 'tender':
                    uuid = release['tender']['RFTUUID']
                    yield scrapy.Request(
                        'https://tenders.nsw.gov.au/?event=public.api.tender.view&RFTUUID=%s' % uuid,
                        meta={'kf_filename': 'tender-%s.json' % uuid},
                        callback=self.parse
                    )
                if response.request.meta['release_type'] == 'contract':
                    for award in release['awards']:
                        uuid = award['CNUUID']
                        yield scrapy.Request(
                            'https://tenders.nsw.gov.au/?event=public.api.contract.view&CNUUID=%s' % uuid,
                            meta={'kf_filename': 'contract-%s.json' % uuid},
                            callback=self.parse
                        )

        else:
            yield {
                'success': False,
                'file_name': hashlib.md5(response.request.url.encode('utf-8')).hexdigest() + '.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="release_package")

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
