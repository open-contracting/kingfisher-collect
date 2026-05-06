import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import parameters


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

    # Local
    base_url = "https://gpip.aac.moj.gov.tw/cht/"

    async def start(self):
        yield scrapy.Request(f"{self.base_url}index.php?code=list&ids=6&page=1", callback=self.parse_list)

    def parse_list(self, response):
        # The listing page mixes PDF/ODS guidance documents and the OCDS JSON file.
        # There is only one file at present, but we check all pages in case they add multiple files in the future.
        # The OCDS file is the only link whose title contains "OCDS".
        for href in response.xpath('//a[contains(@title, "OCDS")]/@href').getall():
            yield self.build_request(f"{self.base_url}{href}", formatter=parameters("ids"))
        # On the last page, the 下一頁 ("next page") anchor is rendered with href="#",
        # so check for a real link before following it.
        next_page = response.xpath('//a[@title="下一頁" and @href!="#"]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_list)
