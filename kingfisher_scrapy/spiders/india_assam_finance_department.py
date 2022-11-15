import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class IndiaAssamFinanceDepartment(SimpleSpider):
    """
    Domain
      Assam State Government Finance Department - Open Government Data (OGD) Platform India
    Bulk download documentation
      https://data.gov.in/catalog/assam-public-procurement-data
    """
    name = 'india_assam_finance_department'

    # BaseSpider
    unflatten = True

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('https://data.gov.in/backend/dmspublic/v1/resources?filters['
                             'catalog_reference]=7259310&offset=0&limit=100&filters[domain_visibility]=4',
                             meta={'file_name': 'response.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for row in data['data']['rows']:
            yield scrapy.Request(row['datafile'][0], meta={'file_name': f"{row['title'][0]}.csv"})
