import hashlib
import json
import requests
import scrapy
from math import ceil

from kingfisher_scrapy.base_spider import BaseSpider


class Uganda(BaseSpider):
    name = 'uganda_releases'
    download_delay = 0.9
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        url = 'https://gpp.ppda.go.ug/adminapi/public/api/open-data/v1/releases/planning?fy={}&pde={}'
        url_pdes = 'https://gpp.ppda.go.ug/adminapi/public/api/pdes?page={}'
        pdes_fdy_checks = []

        if self.is_sample():
            total_pages = 1
        else:
            pages = requests.get('https://gpp.ppda.go.ug/adminapi/public/api/pdes')
            total_pages = pages.json()['data']['last_page']

        for page_number in range(1, total_pages + 1):
            data_pdes = requests.get(url_pdes.format(page_number))
            list_pdes = data_pdes.json()['data']['data']
            for i in range(0, len(list_pdes)):
                pde_plans = list_pdes[i]['procurement_plans']
                for j in range(0, len(pde_plans)):
                    financial_year = pde_plans[j]['financial_year']
                    procurement_entity_id = pde_plans[j]['pde_id']
                    pdes_fdy = financial_year + '&' + procurement_entity_id

                    if pdes_fdy not in pdes_fdy_checks:
                        pdes_fdy_checks.append(pdes_fdy)
                        yield scrapy.Request(
                            url.format(financial_year, procurement_entity_id),
                            meta={'kf_filename': hashlib.md5(
                                (url + str(pdes_fdy)).encode('utf-8')).hexdigest() + '.json'}
                        )
                        if self.is_sample():
                            break

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())
            if len(json.dumps(json_data.get('releases')).encode()) > 2:
                yield self.save_data_to_disk(
                    json.dumps(json_data).encode(),
                    response.request.meta['kf_filename'],
                    data_type='release_package',
                    url=response.request.url
                )
            else:
                yield {
                    'success': False,
                    'file_name': response.request.meta['kf_filename'],
                    'url': response.request.url,
                    'errors': 'Empty release'
                }
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
