import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider, browser_user_agent
from kingfisher_scrapy.util import handle_http_error, parameters


class NigeriaGombeState(SimpleSpider):
    """
    Domain
      Nigeria Gombe State Open Contracting Portal
    """
    name = 'nigeria_gombe_state'
    user_agent = browser_user_agent
    base_url = 'http://gombe.stateopencontracting.com/{}'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = self.base_url.format('Other-Basic/Report/Json-Report')
        yield scrapy.Request(url, meta={'file_name': 'page-0.html', 'page': 0}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        pattern = '//table[@id="dnn_ctr561_no_JsonReport_DGno_Proc_PlanningPublished"]'\
                  '//tr[position()>1]/td[position()=1 and string-length(text())>1]/text()'
        for item in response.xpath(pattern).getall():
            yield self.build_request(self.base_url.format(f'ocdsjson.ashx?ocid={item}'), formatter=parameters('ocid'))
