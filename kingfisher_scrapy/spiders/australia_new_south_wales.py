from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class AustraliaNewSouthWales(SimpleSpider):
    """
    Domain
      New South Wales (NSW)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2003-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    API documentation
      https://github.com/NSW-eTendering/NSW-eTendering-API/wiki
    """
    name = 'australia_new_south_wales'

    # BaseSpider
    date_format = 'date'
    default_from_date = '2003-01-01'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    url_prefix = 'https://www.tenders.nsw.gov.au/?event=public.api.'
    format_string = f'{url_prefix}{{release_type}}.search&ResultsPerPage=1000'

    def start_requests(self):
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            self.format_string += f'&publishedFrom={from_date}&publishedTo={until_date}'
        for release_type in ('planning', 'tender', 'contract'):
            yield self.build_request(
                self.format_string.format(release_type=release_type),
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
                    f'{self.url_prefix}planning.view&PlannedProcurementUUID={uuid}',
                    formatter=parameters('event', 'PlannedProcurementUUID')
                )
            elif release_type == 'tender':
                uuid = release['tender']['RFTUUID']
                yield self.build_request(
                    f'{self.url_prefix}tender.view&RFTUUID={uuid}',
                    formatter=parameters('event', 'RFTUUID')
                )
            elif release_type == 'contract':
                for award in release['awards']:
                    uuid = award['CNUUID']
                    yield self.build_request(
                        f'{self.url_prefix}contract.view&CNUUID={uuid}',
                        formatter=parameters('event', 'CNUUID')
                    )
