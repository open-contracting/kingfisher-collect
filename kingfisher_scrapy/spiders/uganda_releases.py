import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Uganda(BaseSpider):
    name = 'uganda_releases'
    download_delay = 0.9

    def start_requests(self):
        yield scrapy.Request(
            'https://gpp.ppda.go.ug/adminapi/public/api/pdes',
            meta={'kf_filename': 'start_requests'},
            callback=self.parse_pages
        )

    def parse_pages(self, response):
        if response.status == 200:
            url_pdes = 'https://gpp.ppda.go.ug/adminapi/public/api/pdes?page={}'

            if self.sample:
                total_pages = 1
            else:
                json_data = json.loads(response.text)
                total_pages = json_data['data']['last_page']

            for page_number in range(total_pages):
                yield scrapy.Request(
                    url_pdes.format(page_number + 1),
                    meta={'kf_filename': 'pages_requests'},
                    callback=self.parse_data
                )
        else:
            yield self.build_file_error_from_response(response)

    def parse_data(self, response):
        if response.status == 200:
            url = 'https://gpp.ppda.go.ug/adminapi/public/api/open-data/v1/releases/{}?fy={}&pde={}'
            tags = ['planning', 'tender', 'award', 'contract']
            pdes_fdy_checks = []

            json_data = json.loads(response.text)
            list_pdes = json_data['data']['data']

            for pdes in list_pdes:
                pde_plans = pdes['procurement_plans']

                for plans in pde_plans:
                    financial_year = plans['financial_year']
                    procurement_entity_id = plans['pde_id']
                    pdes_fdy = financial_year + '&' + procurement_entity_id

                    if pdes_fdy not in pdes_fdy_checks:
                        pdes_fdy_checks.append(pdes_fdy)

                        for tag in tags:
                            yield scrapy.Request(
                                url.format(tag, financial_year, procurement_entity_id),
                                meta={'kf_filename': hashlib.md5(
                                    (url + str(pdes_fdy + tag)).encode('utf-8')).hexdigest() + '.json'}
                            )
                            if self.sample:
                                break
                        if self.sample:
                            break
        else:
            yield self.build_file_error_from_response(response)

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type='release_package'
            )

        else:
            yield self.build_file_error_from_response(response)
