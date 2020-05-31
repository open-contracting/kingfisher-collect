import hashlib

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_error


class NigeriaPortal(SimpleSpider):
    """
    Spider arguments
      sample
        Download only the first release package in the dataset.
    """
    name = 'nigeria_portal'
    data_type = 'release_package'

    download_delay = 0.9
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'  # noqa: E501

    def start_requests(self):
        yield scrapy.Request(
            'http://nocopo.bpp.gov.ng/OpenData.aspx',
            meta={'kf_filename': 'list.html'},
            callback=self.parse_list
        )

    @handle_error
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
                if self.sample:
                    break

        yield scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            meta={'kf_filename': hashlib.md5(response.url.encode('utf-8')).hexdigest() + '.json'}
        )
