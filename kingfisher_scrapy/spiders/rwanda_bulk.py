from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components, date_range_by_year, handle_http_error


class RwandaBulk(CompressedFileSpider):
    """
    Domain
      Rwanda Public Procurement Authority (RPPA)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2016-06'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    Bulk download documentation
      https://ocds.umucyo.gov.rw/OpenData
    """

    name = "rwanda_bulk"

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2016-06"
    date_required = True
    skip_pluck = "Already covered (see code for details)"  # rwanda_api

    # SimpleSpider
    data_type = "release_package"

    def start_requests(self):
        for year in date_range_by_year(self.from_date.year, self.until_date.year):
            # The month parameter only works with the value "n/a"
            url = f"https://ocds.umucyo.gov.rw/core/api/v1/portal/dataset?year={year}&month=n/a"
            yield scrapy.Request(url, meta={"file_name": f"list_{year}.json"}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        """
        The response looks like:

        {
            "year": "2024 n/a",
            "Dataset": [
                {
                    "data_name": "2024-01",
                    "details": "1589741",
                    "format": "json",
                    "size": "",
                    "json_url": "https://ocds.umucyo.gov.rw/core/api/v1/portal/download-file/2024/01/2024-01-json.zip",
                    "csv_url": "https://ocds.umucyo.gov.rw/core/api/v1/portal/download-file/2024/01/2024-01-csv.zip",
                    "xls_url": "https://ocds.umucyo.gov.rw/core/api/v1/portal/download-file/2024/01/2024-01-xlsx.zip",
                    "fiscal_year": "2024",
                    "release_date": "2024-11-17 13:01:57.208380"
                },
            ...
        }
        """
        for item in response.json()["Dataset"]:
            date = datetime.strptime(item["data_name"], "%Y-%m").replace(tzinfo=self.from_date.tzinfo)
            if not (self.from_date <= date <= self.until_date):
                continue

            yield self.build_request(item["json_url"], formatter=components(-1))
