import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import browser_user_agent, handle_http_error


class Croatia(CompressedFileSpider):
    """
    Domain
      Elektronički oglasnik javne nabave (Electronic public procurement notices)
    Bulk download documentation
      https://eojn.nn.hr/SPIN/application/ipn/Oglasnik/PreuzimanjeUgovoraOCD.aspx
    """
    name = 'croatia'
    download_delay = 1
    user_agent = browser_user_agent

    # BaseSpider
    check_json_format = True

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

        for file_id in sorted(response.xpath('//td/a/@id').getall(), reverse=True):
            yield scrapy.FormRequest.from_response(
                response,
                clickdata={'id': file_id},
                meta={'file_name': 'list.zip'},
                formdata={
                    '__EVENTTARGET': file_id.replace('_', '$'),
                    '__EVENTARGUMENT': '',
                },
            )
