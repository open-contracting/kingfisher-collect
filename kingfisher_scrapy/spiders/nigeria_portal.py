import hashlib

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class NigeriaPortal(BaseSpider):
    name = 'nigeria_portal'
    start_urls = ['http://nocopo.bpp.gov.ng/OpenData.aspx']
    download_delay = 0.9
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'  # noqa: E501

    @handle_error()
    def parse(self, response):
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
            meta={'kf_filename': hashlib.md5(response.url.encode('utf-8')).hexdigest() + '.json'},
            callback=self.parse_post
        )

    @handle_error()
    def parse_post(self, response):
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type='release_package'
        )
