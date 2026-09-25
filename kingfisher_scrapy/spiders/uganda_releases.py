import orjson
import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import date_range_by_year


class UgandaReleases(SimpleSpider):
    """
    Domain
      Government Procurement Portal (GPP) - Public Procurement and Disposal of Public Assets Authority (PPDA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2015'.
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
    custom_settings = {
        # Poll one export job at a time.
        "CONCURRENT_REQUESTS": 1,
        # Returns HTTP 403 if too many requests. (1 is too short.)
        "DOWNLOAD_DELAY": 2,
    }

    # BaseSpider
    date_format = "year"
    date_required = True
    default_from_date = "2015"

    # SimpleSpider
    data_type = "release_package"

    url_prefix = "https://cdn.ppda.go.ug/api/open-data/v2/ocds/"
    # Seconds to wait before each poll, honored by DelayedRequestMiddleware.
    poll_wait_time = 30
    max_polls = 20

    async def start(self):
        # The download is asynchronous: create an export job, poll its status, then download the file.
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
            yield self.build_request(
                data["status_url"],
                formatter=None,
                meta={
                    "file_name": response.request.meta["file_name"],
                    "wait_time": self.poll_wait_time,
                },
                callback=self.parse_status,
            )
        else:
            self.log_error_from_response(response, message=data)

    def parse_status(self, response):
        data = response.json()
        meta = response.request.meta
        match data.get("status"):
            case "complete":
                yield self.build_request(data["download_url"], formatter=None, meta={"file_name": meta["file_name"]})
            case "queued" | "processing":
                polls = meta.get("polls", 0) + 1
                if polls > self.max_polls:
                    self.log_error_from_response(response, message=f"Gave up polling (polled {polls} times)")
                    return
                request = response.request.copy()
                request.meta["polls"] = polls
                request.dont_filter = True
                yield request
            case _:
                self.log_error_from_response(response, message=data)
