import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import (append_path_components, browser_user_agent, components, handle_http_error, join,
                                    parameters, replace_parameters)


class Ukraine(SimpleSpider):
    """
    Domain
      ProZorro OpenProcurement API
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2016-01-01T00:00:00'.
    API documentation
      https://prozorro-api-docs.readthedocs.io/uk/latest/tendering/index.html
    """
    name = 'ukraine'
    user_agent = browser_user_agent  # to avoid HTTP 412 errors

    # BaseSpider
    encoding = 'utf-16'
    data_type = 'release_package'
    date_format = 'datetime'
    default_from_date = '2016-01-01T00:00:00'
    date_required = True

    def start_requests(self):
        # A https://public.api.openprocurement.org/api/0/contracts endpoint also exists but the data returned from
        # there is already included in the tenders endpoint. If we would like to join both, the tender_id field from
        # the contract endpoint can be used with the id field from the tender endpoint.
        url = 'https://public-api.prozorro.gov.ua/api/2.5/tenders'
        if self.from_date:
            url = f'{url}?offset={self.from_date.strftime(self.date_format)}'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()

        for item in data['data']:
            url = f"{append_path_components(replace_parameters(response.request.url, offset=None), item['id'])}" \
                  "?opt_schema=ocds"
            yield self.build_request(url, formatter=components(-2))

        yield self.build_request(data['next_page']['uri'], formatter=join(components(-1), parameters('offset')),
                                 callback=self.parse_list)
