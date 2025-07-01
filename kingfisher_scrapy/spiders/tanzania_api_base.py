import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider


class TanzaniaAPIBase(IndexSpider):
    # BaseSpider
    root_path = 'content.item'

    # IndexSpider
    page_count_pointer = '/totalPages'
    start_page = 0
    param_limit = 'pageSize'

    def start_requests(self):
        yield scrapy.Request(f'https://nest.go.tz/gateway/nest-data-portal-api/api/{self.data_type}s?page=0&pageSize=10'
                             , meta={'file_name': 'page-0.json'}, callback=self.parse_list)
