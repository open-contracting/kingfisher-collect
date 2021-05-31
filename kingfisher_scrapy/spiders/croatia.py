import re

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider, browser_user_agent
from kingfisher_scrapy.util import handle_http_error


class CroatiaPortal(CompressedFileSpider):
    """
        Domain
          Open data from the register of contracts from the Electronic Public
        Procurement Notice of the Republic of Croatia
    """

    name = 'croatia'
    download_delay = 0.9
    user_agent = browser_user_agent

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://eojn.nn.hr/SPIN/application/ipn/Oglasnik/PreuzimanjeUgovoraOCD.aspx',
            meta={'file_name': 'page-0.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):

        for id in response.xpath('//td/a/@id').getall():
            yield scrapy.FormRequest.from_response(
                response,
                clickdata={'id': id},
                meta={'file_name': 'list.zip'},
                formdata={
                    '__EVENTTARGET': id.replace('_', '$'),
                    '__EVENTARGUMENT': '',
                },
            )
