import datetime

import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT, handle_http_error, parameters


class RwandaBulk(CompressedFileSpider):
    """
    Domain
      Rwanda Public Procurement Authority (RPPA)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2013-12'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    Bulk download documentation
      https://ocds.umucyo.gov.rw/OpenData
    """

    name = "rwanda_bulk"
    download_timeout = MAX_DOWNLOAD_TIMEOUT

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2013-12"
    skip_pluck = "Already covered (see code for details)"  # rwanda_api

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request(
            "https://ocds.umucyo.gov.rw/opendata/api/v1/ui/data_set/available_datasets",
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        """
        The response looks like:
        {
            "status": 200,
            "returnCode": 7,
            "message": "Available datasets successfully retrieved",
            "datasets": {
                "2025": [
                    "01-January-csv.zip",
                    "01-January-json.zip",
                    "01-January-xlsx.zip",
                    "02-February-csv.zip",
                    "02-February-json.zip",
                    "02-February-xlsx.zip",
                    ...,
                    "flattened",
                    "json"
                ],
                ...
            }
        }
        """
        for year, datasets in response.json()["datasets"].items():
            for item in datasets:
                if item.endswith("-json.zip"):
                    if self.from_date and self.until_date:
                        date = datetime.datetime(int(year), int(item[:2]), 1, tzinfo=datetime.timezone.utc)
                        if not (self.from_date <= date <= self.until_date):
                            continue
                    yield self.build_request(
                        f"https://ocds.umucyo.gov.rw/opendata/api/v1/ui/data_set/download?year={year}&month_file={item}",
                        formatter=parameters("year", "month_file"),
                    )
