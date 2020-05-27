import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Moldova(BaseSpider):
    name = 'moldova'

    endpoints = {"budgets": "https://public.mtender.gov.md/budgets/",
                 # From https://github.com/open-contracting/kingfisher-collect/issues/192#issuecomment-529928683
                 # The /tenders/plans endpoint appeared to return exactly the same data as the /tenders endpoint except
                 # that when given an OCID parameter it returned an error message. It may be that /tenders/plans just
                 # lists a subset of /tenders but this isn't clear.
                 # "plans": "https://public.mtender.gov.md/tenders/plan/",
                 "tenders": "https://public.mtender.gov.md/tenders/"}

    def start_requests(self):
        for endpoint, url in self.endpoints.items():
            yield scrapy.Request(
                url=url,
                meta={'kf_filename': 'meta-{}-start.json'.format(endpoint), 'endpoint': endpoint, 'data': False}
            )

    def parse(self, response):
        if response.status == 200:
            if response.request.meta['data']:
                yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                    data_type='record_package')
            else:
                self.build_file_from_response(response, response.request.meta['kf_filename'])
                json_data = json.loads(response.text)
                offset = json_data.get('offset')
                # not having an offset in the data means the data has come to an end.
                if not offset:
                    return

                endpoint = response.request.meta['endpoint']
                endpoint_url = self.endpoints[endpoint]

                for data in json_data.get('data', []):
                    yield scrapy.Request(
                        url=endpoint_url + data['ocid'],
                        meta={
                            'kf_filename': 'data-{}-{}.json'.format(endpoint, data['ocid']),
                            'endpoint': endpoint,
                            'data': True,
                        }
                    )

                if self.sample:
                    return

                yield scrapy.Request(
                    url=endpoint_url + '?offset=' + offset,
                    meta={
                        'kf_filename': 'meta-{}-{}.json'.format(endpoint, offset),
                        'endpoint': endpoint,
                        'data': False,
                    }
                )

        else:
            yield self.build_file_error_from_response(response)
