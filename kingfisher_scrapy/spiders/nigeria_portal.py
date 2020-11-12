import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider, browser_user_agent
from kingfisher_scrapy.util import handle_http_error


class NigeriaPortal(SimpleSpider):
    """
    Domain
      Nigeria Open Contracting Portal (NOCOPO) of Bureau of Public Procurement (BPP)
    """
    name = 'nigeria_portal'
    data_type = 'release_package'

    download_delay = 0.9
    user_agent = browser_user_agent

    def start_requests(self):
        yield scrapy.Request(
            'http://nocopo.bpp.gov.ng/OpenData.aspx',
            meta={'file_name': 'form.html', 'page': 0},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        page = response.request.meta['page']
        data = {
            'dnn$ctr561$no_JsonReport$lbtnExportAll': 'Export Checked to JSON',
        }

        checks = response.css('input').xpath('@name').getall()
        for item in checks:
            if 'dnn$ctr' in item and 'chbIsDoing' in item:
                data.update({item: 'on'})

        # '__VIEWSTATE', '__EVENTVALIDATION' and others fields are required in order to scrape ASP.net webpages
        # scrapy.FormRequest.from_response() will autofill a form based on the response data of the previous request.
        # We can then override or add fields because it stores the formdata as a dict.
        yield scrapy.FormRequest.from_response(
            response,
            formdata=data,
            meta={'file_name': 'page{}.json'.format(page)}
        )

        # We only try with the first 20 pages, later we will have another problem because the numbers at the end of the
        # values in '__EVENTTARGET': '{:02d}' are in a cycle, so the button that takes us to page 2 and page 21, passes
        # the same parameters to the JS function __doPostBack().
        if page == 20:
            # page = 00 restart the cycle
            return

        # __doPostBack() JS function sets the values for '__EVENTTARGET' and '__EVENTARGUMENT' when clicking other pages
        yield scrapy.FormRequest.from_response(
            response,
            formdata={
                '__EVENTTARGET':
                    'dnn$ctr561$no_JsonReport$DGno_Proc_PlanningPublished$ctl104$ctl{:02d}'.format(page + 1),
                '__EVENTARGUMENT': '',
            },
            meta={'file_name': 'page{}.json', 'page': page + 1},
            callback=self.parse_list
        )
