from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, get_parameter_value


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
        yield self.build_request("https://www.just.ro/ocds/", formatter=components(-1), callback=self.parse_list)

    def parse_list(self, response):
        # Each year is an accordion item, titled like "OCDS - 2025", embedding its folder as an iframe.
        for item in response.xpath('//div[contains(concat(" ", @class, " "), " brz-accordion__item ")]'):
            title = item.xpath('.//span[contains(@class, "brz-accordion__nav-title")]/text()').get("")
            src = item.xpath(".//iframe/@src").get()
            if not title.startswith("OCDS") or not src:
                continue
            if self.from_date and self.until_date:
                year = int(title.rsplit(" ", 1)[1])
                if not (self.from_date.year <= year <= self.until_date.year):
                    continue
            yield self.build_folder_request(get_parameter_value(src, "idFolder"))

    def parse_folder(self, response):
        data = response.json()
        for folder in data["dirLinkList3"]["dirLink3"]:
            yield self.build_folder_request(folder["id"])
        for file in data["dirLink"]["fileLinks"]:
            if file["extension"] == "json":
                # The download URL ends in an opaque token, so use the file name instead.
                yield self.build_request(file["downloadLink"], formatter=None, meta={"file_name": file["name"]})

    def build_folder_request(self, folder_id):
        return self.build_request(
            f"https://www.just.ro/mj-dmsws/int-mj/getSubFolders3AndLinkById/{folder_id}",
            formatter=components(-1),
            callback=self.parse_folder,
        )
