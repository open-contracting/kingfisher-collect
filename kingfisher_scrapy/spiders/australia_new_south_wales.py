from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class AustraliaNewSouthWales(SimpleSpider):
    """
    Domain
      New South Wales (NSW)
    API documentation
      https://github.com/NSW-eTendering/NSW-eTendering-API/blob/master/README.md
    """
    name = 'australia_new_south_wales'

    base_url = 'https://www.tenders.nsw.gov.au/?event=public.api.'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        for release_type in ('planning', 'tender', 'contract'):
            yield self.build_request(
                f'{self.base_url}{release_type}.search&ResultsPerPage=1000',
                formatter=parameters('event'),
                meta={'release_type': release_type},
                callback=self.parse_list
            )

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        release_type = response.request.meta['release_type']

        if data['releases'] and 'links' in data and isinstance(data['links'], dict) and 'next' in data['links']:
            yield self.build_request(
                data['links']['next'],
                formatter=parameters('event', 'startRow'),
                meta={'release_type': release_type},
                callback=self.parse_list
            )

        for release in data['releases']:
            if release_type == 'planning':
                uuid = release['tender']['plannedProcurementUUID']
                yield self.build_request(
                    f'{self.base_url}planning.view&PlannedProcurementUUID={uuid}',
                    formatter=parameters('event', 'PlannedProcurementUUID')
                )
            elif release_type == 'tender':
                uuid = release['tender']['RFTUUID']
                yield self.build_request(
                    f'{self.base_url}tender.view&RFTUUID={uuid}',
                    formatter=parameters('event', 'RFTUUID')
                )
            elif release_type == 'contract':
                for award in release['awards']:
                    uuid = award['CNUUID']
                    yield self.build_request(
                        f'{self.base_url}contract.view&CNUUID={uuid}',
                        formatter=parameters('event', 'CNUUID')
                    )
