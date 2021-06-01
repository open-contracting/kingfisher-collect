import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider, browser_user_agent
from kingfisher_scrapy.util import handle_http_error


class Croatia(CompressedFileSpider):
    """
        Domain
          Electronic Public Procurement Classifieds of the Republic of Croatia
        Bulk download documentation
          https://eojn.nn.hr/SPIN/application/ipn/Oglasnik/PreuzimanjeUgovoraOCD.aspx
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
