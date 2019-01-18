import json

import scrapy


class Armenia(scrapy.Spider):
    name = 'australia_nsw'

    def start_requests(self):
        sample = hasattr(self, 'sample') and self.sample == 'true'
        release_types = ['planning', 'tender', 'contract']
        url = 'https://tenders.nsw.gov.au'
        url += '/?event=public.api.%s.search&ResultsPerPage=1000'
        if sample:
            release_types = ['planning']
        for r in release_types:
            yield scrapy.Request(url % r, meta={'data_type': 'meta', 'release_type': r})

    def parse(self, response):
        sample = hasattr(self, 'sample') and self.sample == 'true'
        json_data = json.loads(response.body_as_unicode())
        data_type = response.meta['data_type']
        release_type = response.meta['release_type']
        if data_type == 'meta':
            stage_urls = []
            if 'links' in json_data and 'next' in json_data['links'] and not sample:
                stage_urls.append(json_data['links']['next'])

            for release in json_data['releases']:
                    if release_type == 'planning':
                        uuid = release['tender']['plannedProcurementUUID']
                        stage_urls.append('https://tenders.nsw.gov.au/?event=public.api.planning.view'
                                          '&PlannedProcurementUUID=%s' % uuid)
                    if release_type == 'tender':
                        uuid = release['tender']['RFTUUID']
                        stage_urls.append('https://tenders.nsw.gov.au/?event=public.api.tender.view&RFTUUID=%s' % uuid)
                    if release_type == 'contract':
                        for award in release['awards']:
                            uuid = award['CNUUID']
                            stage_urls.append('https://tenders.nsw.gov.au/?event=public.api.contract.view&CNUUID=%s'
                                              % uuid)
            for url in stage_urls:
                yield scrapy.Request(url, meta={'data_type': 'release_package', 'release_type': release_type})
        else:
            yield {
                'file_urls': [response.url],
                'data_type': 'release-package',
                'release_type': release_type
            }
