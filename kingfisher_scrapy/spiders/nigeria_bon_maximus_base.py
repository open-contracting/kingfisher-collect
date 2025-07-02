import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, get_parameter_value, handle_http_error


class NigeriaBonMaximusBase(SimpleSpider):
    # SimpleSpider
    data_type = "release_package"

    # url_prefix must be provided by subclasses.

    def start_requests(self):
        url = f"{self.url_prefix}awarded_contracts.php"
        yield scrapy.Request(url, meta={"file_name": "list.html"}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath('//table[@id="contractTable"]/tbody/tr/td[2]/a/@href').getall():
            # The URLs look like
            # https://url_prefix/existing_award_details.php?id=ocds-xwwr9a-000103-OS/HLT/02
            ocid = get_parameter_value(url, "id").replace("/", "_")
            yield self.build_request(f"{self.url_prefix}media/{ocid}.json", formatter=components(-1))
