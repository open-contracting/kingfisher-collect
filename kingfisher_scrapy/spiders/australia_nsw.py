import json
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


# This Spider uses the old system of pipelines! DO NOT USE IT AS AN EXAMPLE OF WHAT TO DO IN FUTURE SPIDERS!
# Thank you.
class AustraliaNSW(BaseSpider):
    name = 'australia_nsw'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.OldKingfisherFilesPipeline': 400,
            'kingfisher_scrapy.pipelines.OldKingfisherPostPipeline': 800,
        }
    }

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
            if sample:
                stage_urls = [stage_urls[0]]

            for url in stage_urls:
                yield scrapy.Request(url, meta={'data_type': 'release_package', 'release_type': release_type})
        else:
            yield {
                'file_urls': [response.url],
                'data_type': 'release_package',
                'release_type': release_type
            }
