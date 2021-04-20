import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters, replace_parameters


class Moldova(SimpleSpider):
    """
    Domain
      MTender
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
    """
    name = 'moldova'

    # SimpleSpider
    data_type = 'release_package'

    # BaseSpider
    date_format = 'datetime'
    default_from_date = '2018-10-18T00:00:00'
    date_required = True

    def start_requests(self):
        # https://public.mtender.gov.md offers three endpoints: /tenders/, /tenders/plan/ and /budgets/. However, this
        # service publishes contracting processes under multiple OCIDs.
        #
        # The http://public.eprocurement.systems/ocds/ service instead publishes contracting processes under one OCID.
        # However, it has no endpoint to list OCIDs.
        #
        # As such, we retrieve OCIDs from the first, and data from the second.
        #
        # Note: The OCIDs from the /budgets/ endpoint have no corresponding data in the second service. The OCIDs from
        # the /tenders/plan/ endpoint are the same as from the /tenders/ endpoint.
        url = f'https://public.mtender.gov.md/tenders/?offset={self.from_date.strftime(self.date_format)}'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        base_url = 'http://public.eprocurement.systems/ocds/tenders/'
        data = response.json()
        # The last page returns an empty JSON object.
        if not data:
            return

        for item in data['data']:
            url = replace_parameters(base_url, offset=None) + item['ocid']
            yield self.build_request(url, formatter=components(-2))

        url = replace_parameters(response.request.url, offset=data['offset'])
        yield self.build_request(url, formatter=join(components(-1), parameters('offset')), callback=self.parse_list)
