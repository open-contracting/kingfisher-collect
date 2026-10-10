import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import KingfisherScrapyError
from kingfisher_scrapy.util import get_parameter_value


class RomaniaMinistryOfJustice(SimpleSpider):
    """
    Domain
      Ministerul Justiției (Ministry of Justice)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2022'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://www.just.ro/ocds/
    """

    name = "romania_ministry_of_justice"

    # BaseSpider
    date_format = "year"
    default_from_date = "2022"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request("https://www.just.ro/ocds/", callback=self.parse_list)

    def parse_list(self, response):
        # The page has one accordion per year, with a title like "OCDS - 2025", listing a folder in an iframe.
        for iframe in response.xpath('//iframe[contains(@src, "idFolder")]'):
            year = int(iframe.xpath("preceding::span[1]/text()").get().removeprefix("OCDS - "))
            if self.from_date and self.until_date and not (self.from_date.year <= year <= self.until_date.year):
                continue
            folder_id = get_parameter_value(iframe.attrib["src"], "idFolder")
            yield scrapy.Request(
                f"https://www.just.ro/mj-dmsws/int-mj/getSubFolders3AndLinkById/{folder_id}",
                callback=self.parse_folder,
            )

    def parse_folder(self, response):
        data = response.json()
        if data["dirLinkList3"]["dirLink3"]:
            raise KingfisherScrapyError(f"Unexpected subfolders in {response.url}")
        for file in data["dirLink"]["fileLinks"]:
            if file["extension"] != "json":
                raise KingfisherScrapyError(f"Unexpected extension in {response.url}: {file['extension']!r}")
            # The download URL ends in an opaque token, so use the file name instead.
            yield self.build_request(file["downloadLink"], formatter=None, meta={"file_name": file["name"]})
