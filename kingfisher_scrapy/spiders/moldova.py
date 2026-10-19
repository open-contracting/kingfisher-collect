import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.exceptions import RetryableError
from kingfisher_scrapy.util import components, replace_parameters


class Moldova(BaseSpider):
    """
    Domain
      MTender
    Caveats
      OCIDs are listed from ``https://public.mtender.gov.md/tenders/plan/``, which publishes contracting processes
      under multiple OCIDs, and data is downloaded from ``http://public.eprocurement.systems/ocds/tenders/{ocid}``,
      which publishes contracting processes under one OCID but has no endpoint to list OCIDs.
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
    """

    name = "moldova"

    # BaseSpider
    date_format = "datetime"

    # SimpleSpider
    data_type = "release_package"

    # Local
    # The /tenders/ endpoint returns empty responses, and the /tenders/plan/ endpoint has the same OCIDs.
    list_url = "https://public.mtender.gov.md/tenders/plan/"
    base_url = "http://public.eprocurement.systems/ocds/tenders/"

    async def start(self):
        if self.from_date:
            url = f"{self.list_url}?offset={self.from_date.strftime(self.date_format)}"
        else:
            url = self.list_url
        yield scrapy.Request(url, callback=self.parse_list)

    def load_json_or_retry_error(self, response):
        r"""
        Retry an HTTP 200 response if its body is empty or describes an error, like:

        {
          "message": "connect EHOSTUNREACH 185.108.182.236:443",
          "name": "Error",
          "stack": "Error: connect EHOSTUNREACH 185.108.182.236:443\n    at TCPConnectWrap.afterConnect...",
          "config": {
            "url": "https://public.mtender.gov.md/tenders/ocds-b3wdp1-MD-1603913785143",
            "method": "get",
            "headers": {
              "Accept": "application/json, text/plain, */*",
              "User-Agent": "axios/0.21.1"
            },
            "transformRequest": [
              null
            ],
            "transformResponse": [
              null
            ],
            "timeout": 0,
            "xsrfCookieName": "XSRF-TOKEN",
            "xsrfHeaderName": "X-XSRF-TOKEN",
            "maxContentLength": -1,
            "maxBodyLength": -1
          },
          "code": "EHOSTUNREACH"
        }
        """
        if not response.body:
            raise RetryableError
        data = response.json()
        if data.get("name") == "Error":
            raise RetryableError
        return data

    def parse_list(self, response):
        data = self.load_json_or_retry_error(response)

        # The last page returns an empty JSON object.
        if not data:
            return

        for item in data["data"]:
            yield self.build_request(f"{self.base_url}{item['ocid']}", formatter=components(-1))

        yield scrapy.Request(replace_parameters(response.request.url, offset=data["offset"]), callback=self.parse_list)

    def parse(self, response):
        self.load_json_or_retry_error(response)
        yield self.build_file_from_response(response, data_type=self.data_type)
