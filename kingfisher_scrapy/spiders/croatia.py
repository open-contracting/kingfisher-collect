import scrapy
from form2request import form2request

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT


class Croatia(CompressedFileSpider):
    """
    Domain
      Elektronički oglasnik javne nabave (Electronic public procurement notices)
    Bulk download documentation
      https://eojn.nn.hr/SPIN/application/ipn/Oglasnik/PreuzimanjeUgovoraOCD.aspx
    """

    name = "croatia"
    custom_settings = {
        "USER_AGENT": BROWSER_USER_AGENT,
    }

    # BaseSpider
    validate_json = True  # https://github.com/open-contracting/kingfisher-collect/issues/886

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request(
            "https://eojn.nn.hr/SPIN/application/ipn/Oglasnik/PreuzimanjeUgovoraOCD.aspx", callback=self.parse_list
        )

    def parse_list(self, response):
        form = response.xpath("//form")
        for priority, link in enumerate(form.xpath(".//a[@id]")):
            file_id = link.attrib["id"]
            yield form2request(
                form,
                data={
                    "__EVENTTARGET": file_id.replace("_", "$"),
                    "__EVENTARGUMENT": "",
                },
                click=link,
            ).to_scrapy(callback=self.parse, meta={"file_name": f"{file_id}.zip"}, priority=priority)
