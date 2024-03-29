import re

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import browser_user_agent, handle_http_error


class NigeriaGombeState(SimpleSpider):
    """
    Domain
      Nigeria Gombe State Open Contracting Portal
    Bulk download documentation
        http://gombe.stateopencontracting.com/Other-Basic/Report/Json-Report
    """
    name = 'nigeria_gombe_state'
    user_agent = browser_user_agent

    # BaseSpider
    concatenated_json = True

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('http://gombe.stateopencontracting.com/Other-Basic/Report/Json-Report',
                             meta={'file_name': 'page-0.html', 'page': 0}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        self.logger.debug('Crawled page %s', response.xpath('//td[@colspan="8"]/span/text()').get())

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
