import re

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider, browser_user_agent
from kingfisher_scrapy.util import handle_http_error


class NigeriaPortal(SimpleSpider):
    """
    Domain
      Nigeria Open Contracting Portal (NOCOPO) of Bureau of Public Procurement (BPP)
    """
    name = 'nigeria_portal'
    download_delay = 0.9
    user_agent = browser_user_agent

    # SimpleSpider
    data_type = 'release_package'

    concatenated_json = True

    def start_requests(self):
        yield scrapy.Request(
            'http://nocopo.bpp.gov.ng/OpenData.aspx',
            meta={'file_name': 'page-0.html', 'page': 0},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        self.logger.debug('Crawled page {}'.format(response.xpath('//td[@colspan="8"]/span/text()').get()))

        page = response.request.meta['page']

        formdata = {}
        for item in response.xpath('//input/@name').getall():
            if re.search(r'^dnn\$ctr561\$no_JsonReport\$DGno_Proc_PlanningPublished\$ctl\d+\$chbIsDoing$', item):
                formdata[item] = 'on'

        yield scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            clickdata={'name': 'dnn$ctr561$no_JsonReport$lbtnExportAll'},
            meta={'file_name': f'page-{page}.json'},
        )

        # Get the next pagination link, and simulate clicking on it.
        href = response.xpath('//td[@colspan="8"]/span/following-sibling::a[1]/@href').get()
        if href:
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    '__EVENTTARGET': re.search(r"'(.+?)'", href)[1],
                    '__EVENTARGUMENT': '',
                },
                dont_click=True,
                meta={'file_name': f'page-{page}.html', 'page': page + 1},
                callback=self.parse_list,
            )
