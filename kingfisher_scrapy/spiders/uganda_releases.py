from typing import Literal, get_args

import orjson
import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import date_range_by_year

IN_PROGRESS_STATUSES = Literal["queued", "processing", "pending", "running", "in_progress", "started"]


class UgandaReleases(SimpleSpider):
    """
    Domain
      Government Procurement Portal (GPP) - Public Procurement and Disposal of Public Assets Authority (PPDA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2019'.
        The year refers to the start of the fiscal year range, e.g. if ``from_date`` = '2019' then the fiscal year is
        '2019-2020'
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
        The year refers to the start of the fiscal year range, e.g. if ``until_date`` = '2019' then the fiscal year is
        '2019-2020'
    Bulk download documentation
        https://gpp.ppda.go.ug/public/open-data/ocds/ocds-datasets
    """

    name = "uganda_releases"
    # Poll the export status endpoint one request at a time, to avoid overwhelming the server.
    download_delay = 2
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
    }

    # BaseSpider
    date_format = "year"
    date_required = True
    default_from_date = "2019"

    # SimpleSpider
    data_type = "release_package"

    url_prefix = "https://cdn.ppda.go.ug/api/open-data/v2/ocds/"

    async def start(self):
        # The download is asynchronous: POST to create an export job, poll its status, then download the file.
        for year in date_range_by_year(self.from_date.year, self.until_date.year):
            fiscal_year = f"{year}-{year + 1}"
            yield scrapy.Request(
                f"{self.url_prefix}exports",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=orjson.dumps({"fy": fiscal_year, "format": "json"}),
                meta={"file_name": f"{fiscal_year}.json"},
                callback=self.parse_job,
            )

    def parse_job(self, response):
        data = response.json()
        if data.get("success"):
            yield scrapy.Request(
                data["status_url"],
                meta={
                    "file_name": response.request.meta["file_name"],
                    "job_id": data["job_id"],
                    "wait_time": 30,
                },
                callback=self.parse_status,
            )
        else:
            self.logger.error("Export request failed: %r", data)

    def parse_status(self, response):
        data = response.json()
        meta = response.request.meta
        status = data.get("status")
        match status:
            case "failed":
                self.logger.error("Export job %s failed: %s", meta["job_id"], data.get("message"))
            # In-progress statuses indicate the export job is not ready yet, so we keep polling.
            case _ if status in get_args(IN_PROGRESS_STATUSES):
                attempts = meta.get("retries", 0) + 1
                if attempts > 20:
                    self.logger.error("Export job %s not ready after %d polls", meta["job_id"], attempts)
                    return
                request = response.request.copy()
                request.meta["retries"] = attempts
                request.dont_filter = True
                yield request
            case _:
                yield self.build_request(
                    f"{self.url_prefix}exports/{meta['job_id']}/download",
                    formatter=None,
                    meta={"file_name": meta["file_name"]},
                )
