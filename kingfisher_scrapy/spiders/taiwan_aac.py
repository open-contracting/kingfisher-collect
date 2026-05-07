import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import get_parameter_value, parameters, replace_parameters


class TaiwanAAC(SimpleSpider):
    """
    Domain
      Agency Against Corruption, Ministry of Justice, ROC (Taiwan)
    Bulk download documentation
      https://gpip.aac.moj.gov.tw/cht/index.php?code=list&ids=6&page=1
    """

    name = "taiwan_aac"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request(
            "https://gpip.aac.moj.gov.tw/cht/index.php?code=list&ids=6&page=1", callback=self.parse_list
        )

    def parse_list(self, response):
        for href in response.xpath('//a[contains(@title, "OCDS")]/@href').getall():
            yield self.build_request(response.urljoin(href), formatter=parameters("ids"))

        # If the page is out of range, there are no list items.
        if response.xpath('//div[@class="main"]//li'):
            page = int(get_parameter_value(response.request.url, "page"))
            yield scrapy.Request(replace_parameters(response.request.url, page=page + 1), callback=self.parse_list)
