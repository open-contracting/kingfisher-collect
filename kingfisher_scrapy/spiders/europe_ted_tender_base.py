import scrapy

from kingfisher_scrapy.base_spider import IndexSpider


class EuropeTedTenderBase(IndexSpider):
    """
    Domain
      Tenders Electronic Daily (TED) by TenderBase
    API endpoints
      Get releases by page
        Link
          ``http://www.tenderbase.eu/api/releases/?page={page}``
        Parameters
          page
            page number
    """
    name = 'europe_ted_tender_base'

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'release'

    # IndexSpider
    count_pointer = ''
    limit = 10  # unknown page size parameter
    use_page = True
    start_page = 0
    base_url = 'http://www.tenderbase.eu/api/releases/'

    def start_requests(self):
        url = 'http://www.tenderbase.eu/releases/'
        yield scrapy.Request(url, meta={'file_name': 'count.json'}, callback=self.parse_list)

    def parse_list_loader(self, response):
        return int(response.xpath('//div[@class="container my-4"]//span/span/text()').get())
