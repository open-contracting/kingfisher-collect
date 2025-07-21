import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error, json_dumps


class TanzaniaBulkBase(IndexSpider):
    # BaseSpider
    default_from_date = "2022-01-01"

    # IndexSpider
    result_count_pointer = "/recordsFilteredCount"
    limit = 200
    use_page = True
    start_page = 1
    formatter = None
    parse_list_callback = "parse_items"

    # Local
    url_prefix = "https://nest.go.tz/gateway/nest-data-portal-api"
    # WARNING: This class attribute is modified in-place. The invariants that must be upheld are:
    # - The value of any key can be modified in the `start_requests` method.
    # - Only the value of the `page` key can be modified in any other method.
    payload = {
        "page": start_page,
        "pageSize": limit,  # capped to 200
        # Sort by end date in descending order.
        "fields": [{"fieldName": "endDate", "isSortable": True, "orderDirection": "DESC"}],
        # Download daily packages only, not monthly packages.
        "mustHaveFilters": [{"fieldName": "periodType", "operation": "EQ", "value1": "daily"}],
    }

    def start_requests(self):
        self.payload["mustHaveFilters"].append(
            {
                "fieldName": "dataType",
                "operation": "EQ",
                "value1": self.data_type.split("_")[0],  # record or release
            }
        )
        if self.from_date and self.until_date:
            for date_name in ("startDate", "endDate"):
                self.payload["mustHaveFilters"].append(
                    {
                        "fieldName": date_name,
                        "operation": "BTN",
                        "value1": f"{self.from_date.strftime(self.date_format)}T00:00:00",
                        "value2": f"{self.until_date.strftime(self.date_format)}T23:59:59",
                    }
                )
        url, kwargs = self.url_builder(self.start_page, None, None)
        yield scrapy.Request(url, **kwargs, callback=self.parse_list)

    def url_builder(self, value, data, response):
        self.payload["page"] = value
        # This endpoint is undocumented.
        return f"{self.url_prefix}/packages?withMetaData=true", {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": json_dumps(self.payload),
            "meta": {"file_name": f"page-{value}.json"},
        }

    @handle_http_error
    def parse_items(self, response):
        for item in response.json()["data"]:
            # This endpoint is undocumented.
            yield self.build_request(
                f"{self.url_prefix}/api/packages/download/{item['fileName']}", formatter=components(-1)
            )
            # # Otherwise, the first of 200 requests to return is used.
            if self.pluck:
                break
