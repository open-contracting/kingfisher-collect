import scrapy

from kingfisher_scrapy.base_spiders.index_spider import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class UgandaReleases(IndexSpider):
    """
    Domain
      Government Procurement Portal (GPP) of Public Procurement and Disposal of Public Assets Authority (PPDA)
    Caveats
      The domains described in the API documentation must be replaced by https://gpppapi.com
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2017'.
        The year refers to the start of the fiscal year range, e.g. if ``from_date`` = '2017' then the fiscal year is
        '2017-2018'
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
        The year refers to the start of the fiscal year range, e.g. if ``until_date`` = '2017' then the fiscal year is
        '2017-2018'
    API documentation
        https://docs.google.com/spreadsheets/d/10tVioy-VOQa1FwWoRl5e1pMbGpiymA0iycNcoDFkvks/edit#gid=365266172
    """
    name = 'uganda_releases'
    download_delay = 30  # to avoid API 429 error "too many request"
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    date_format = 'year'
    default_from_date = '2017'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    total_pages_pointer = '/data/last_page'
    parse_list_callback = 'parse_data'

    def start_requests(self):
        url = 'https://gpppapi.com/adminapi/public/api/pdes'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_data(self, response):
        pattern = 'https://gpppapi.com/adminapi/public/api/open-data/v1/releases/{}?fy={}&pde={}'

        data = response.json()
        for pdes in data['data']['data']:
            for plans in pdes['procurement_plans']:
                for tag in ('planning', 'tender', 'award', 'contract'):
                    if self.from_date and self.until_date:
                        start_year = int(plans['financial_year'].split('-')[0])
                        if not (self.from_date.year <= start_year <= self.until_date.year):
                            continue
                    yield self.build_request(
                        pattern.format(tag, plans['financial_year'], plans['pde_id']),
                        formatter=join(components(-1), parameters('fy', 'pde'))
                    )
