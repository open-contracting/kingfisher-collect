import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class Uganda(IndexSpider):
    """
    Domain
      Government Procurement Portal (GPP) of Public Procurement and Disposal of Public Assets Authority (PPDA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2017'.
        The year refers to the start of the fiscal year range, e.g. if from_date='2017' then fiscal_year='2017-2018'
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
        The year refers to the start of the fiscal year range, e.g. if until_date='2017' then fiscal_year='2017-2018'
    API documentation
      https://docs.google.com/spreadsheets/d/10tVioy-VOQa1FwWoRl5e1pMbGpiymA0iycNcoDFkvks/edit#gid=365266172
    """
    name = 'uganda_releases'
    download_delay = 30  # to avoid API 429 error "too many request"
    date_format = 'year'
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    default_from_date = '2017'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    total_pages_pointer = '/data/last_page'
    formatter = staticmethod(parameters('page'))
    base_url = 'https://gpppapi.com/adminapi/public/api/pdes'
    yield_list_results = False

    def start_requests(self):
        yield scrapy.Request(
            self.base_url,
            meta={'file_name': 'page-1.json'},
            callback=self.parse_list,
            cb_kwargs={'callback': self.parse_data}
        )

    @handle_http_error
    def parse_data(self, response):
        pattern = 'https://gpppapi.com/adminapi/public/api/open-data/v1/releases/{}?fy={}&pde={}'

        data = response.json()
        for pdes in data['data']['data']:
            for plans in pdes['procurement_plans']:
                for tag in ('planning', 'tender', 'award', 'contract'):
                    if self.from_date and self.until_date:
                        start_year = int(plans['financial_year'].split("-")[0])
                        if not (self.from_date.year <= start_year <= self.until_date.year):
                            continue
                    yield self.build_request(
                        pattern.format(tag, plans['financial_year'], plans['pde_id']),
                        formatter=join(components(-1), parameters('fy', 'pde'))
                    )
