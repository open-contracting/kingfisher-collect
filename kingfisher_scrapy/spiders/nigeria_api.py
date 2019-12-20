import hashlib
import json
import scrapy
import requests

from kingfisher_scrapy.base_spider import BaseSpider


class NigeriaPortal(scrapy.Spider):
    name = 'nigeria_portal'
    start_urls = ['http://nocopo.bpp.gov.ng/OpenData.aspx']
    download_delay = 0.9
    handle_httpstatus_list = [302]
    dont_redirect: True
    user_agent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36']

    def parse(self, response):

        return scrapy.FormRequest.from_response(
                                                response,
                                                formdata={
                                                        '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
                                                        '__VIEWSTATEGENERATOR': 'CA0B0334',
                                                        '__EVENTVALIDATION' : response.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
                                                        'dnn$ctr561$no_JsonReport$DGno_Proc_PlanningPublished$ctl313$chbIsDoing': 'on',
                                                        'dnn$ctr561$no_JsonReport$lbtnExportAll': 'Export Checked to JSON',
                                                    },
                                                callback=self.parse_post
                                                )

    def parse_post(self, response):
        if response.status == 302:
            print(response.headers.get('Location'))
