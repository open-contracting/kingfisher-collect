import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class MexicoINAIBase(SimpleSpider):
    """
    The spiders corresponding to the institutions that work with INAI can inherit from this class. It assumes that all
    responses have the same data type and api pattern.

    #. Set a ``domain_pattern`` class attribute to assign the portal domain with {} in the end of the string
    """
    fiscal_years_api = '/edca/fiscalYears'
    contracts_api = '/edca/contractingprocess/{}'

    # BaseSpider
    root_path = 'arrayReleasePackage.item'
    date_format = 'year'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            self.domain_pattern.format(self.fiscal_years_api),
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        fiscal_years = response.json()['fiscalYears']
        # The response looks like:
        # {
        #   "fiscalYears": [
        #     {
        #       "id": "..",
        #       "year": "..",
        #       "status": "..",
        #       "createdAt": "..",
        #       "updatedAt": "..",
        #     }
        #   ]
        # }
        for fiscal_year_object in fiscal_years:
            fiscal_year = fiscal_year_object['year']
            if self.from_date and self.until_date:
                if not (self.from_date.year <= fiscal_year <= self.until_date.year):
                    continue
            yield self.build_request(self.domain_pattern.format(self.contracts_api.format(fiscal_year)),
                                     formatter=join(components(-1)))
