import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.exceptions import RetryableError
from kingfisher_scrapy.util import components, handle_http_error, replace_parameters


class MoldovaMultiRecord(BaseSpider):
    """
    Domain
      MTender
    Caveats
      The ``https://public.mtender.gov.md/tenders/{ocid}`` endpoint returns a record package in which each record has a
      different ``ocid`` value (as expected), but these actually represent the same contracting process (not expected).
      To fix this, we reformat the record package as a release package, using each record's ``compiledRelease`` as an
      individual release, and replacing the release's ``ocid`` value with the OCID from the URL.

      The compliant OCDS endpoint ``http://public.eprocurement.systems/ocds/tenders/{ocid}`` returns error messages.
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
    """

    name = "moldova_multi_record"

    # BaseSpider
    date_format = "datetime"

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

        yield self.build_file_from_response(response, data_type="release_package", data=data | {"releases": releases})
