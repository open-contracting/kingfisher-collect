import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class KenyaPPRA(SimpleSpider):
    """
    Domain
      Kenya Public Procurement Regulation Authority
    Bulk download documentation
      https://tenders.go.ke/ocds
    """
    name = 'kenya_ppra'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    base_url = 'https://tenders.go.ke/api/ocds'

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}/index?search=&perpage=10&sortby=&order=asc&page=1',
                             meta={'file_name': 'page1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for item in data['data']:
            yield self.build_request(f'{self.base_url}/tenders?download=true&ocds_id={item["id"]}',
                                     formatter=parameters('ocds_id'))
        if data['next_page_url']:
            yield scrapy.Request(data['next_page_url'], meta={'file_name': f'{data["current_page"]+1}.json'},
                                 callback=self.parse_list)
