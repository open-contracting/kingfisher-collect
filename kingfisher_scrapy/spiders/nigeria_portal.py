import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider, browser_user_agent
from kingfisher_scrapy.util import handle_http_error


class NigeriaPortal(SimpleSpider):
    """
    Spider arguments
      sample
        Sets the number of release packages to download.
    """
    name = 'nigeria_portal'
    data_type = 'release_package'

    download_delay = 0.9
    user_agent = browser_user_agent

    def start_requests(self):
        yield scrapy.Request(
            'http://nocopo.bpp.gov.ng/OpenData.aspx',
            meta={'file_name': 'form.html'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        formdata = {
            '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
            '__VIEWSTATEGENERATOR': 'CA0B0334',
            '__EVENTVALIDATION': response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
            'dnn$ctr561$no_JsonReport$lbtnExportAll': 'Export Checked to JSON',
        }

        checks = response.css('input').xpath('@name').getall()
        for item in checks:
            if 'dnn$ctr' in item and 'chbIsDoing' in item:
                formdata.update({item: 'on'})

        yield scrapy.FormRequest.from_response(response, formdata=formdata, meta={'file_name': 'all.json'})
