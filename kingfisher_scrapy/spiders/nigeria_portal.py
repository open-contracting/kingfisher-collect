import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class NigeriaPortal(BaseSpider):
    name = 'nigeria_portal'
    start_urls = ['http://nocopo.bpp.gov.ng/OpenData.aspx']
    download_delay = 0.9
    user_agent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36']

    def parse(self, response):
        if response.status == 200:
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
                    if self.is_sample():
                        break

            yield scrapy.FormRequest.from_response(
                response,
                formdata=formdata,
                meta={'kf_filename': hashlib.md5(response.url.encode('utf-8')).hexdigest() + '.json'},
                callback=self.parse_post
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse_post(self, response):
        if response.status == 200:
            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type='release_package',
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
