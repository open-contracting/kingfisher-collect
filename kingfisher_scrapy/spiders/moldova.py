import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.exceptions import RetryableError
from kingfisher_scrapy.util import components, handle_http_error, replace_parameters


class Moldova(BaseSpider):
    """
    Domain
      MTender
    Caveats
      https://public.mtender.gov.md offers three endpoints: /tenders/, /tenders/plan/ and /budgets/. However, this
      service publishes the same contracting process under multiple OCIDs.
      To fix this, we get the list of tenders OCIDs from /tenders, query record packages and their compiledReleases
      from /tenders/ocid, replace the OCID of each of them with their main OCID, and create a release package instead,
      preserving the record package metadata.
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
    base_url = "https://public.mtender.gov.md/tenders/"

    async def start(self):
        if self.from_date:
            url = f"{self.base_url}?offset={self.from_date.strftime(self.date_format)}"
        else:
            url = self.base_url
        yield scrapy.Request(url, callback=self.parse_list)

    def load_json_or_retry_error(self, response):
        r"""
        Occasional error response with HTTP 200 code, with an empty response, or JSON like:

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
        if not response.body or response.json().get("name") == "Error":
            raise RetryableError
        return response.json()

    @handle_http_error
    def parse_list(self, response):
        data = self.load_json_or_retry_error(response)

        # The last page returns an empty JSON object.
        if not data:
            return

        for item in data["data"]:
            yield self.build_request(f"{self.base_url}{item['ocid']}", formatter=components(-1))

        yield scrapy.Request(replace_parameters(response.request.url, offset=data["offset"]), callback=self.parse_list)

    @handle_http_error
    def parse(self, response):
        data = self.load_json_or_retry_error(response)

        ocid = components(-1)(response.request.url)

        releases = []
        for record in data.pop("records"):
            release = record["compiledRelease"]
            release["ocid"] = ocid
            releases.append(release)

        yield self.build_file_from_response(response, data_type=self.data_type, data=data | {"releases": releases})
