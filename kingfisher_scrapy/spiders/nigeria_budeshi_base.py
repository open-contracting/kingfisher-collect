import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class NigeriaBudeshiBase(SimpleSpider):
    def start_requests(self):
        yield scrapy.Request(
            'https://budeshi.ng/api/project_list',
            meta={'file_name': 'project_list.json'},
            callback=self.parse_list
        )
