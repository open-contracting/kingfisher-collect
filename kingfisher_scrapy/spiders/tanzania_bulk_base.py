import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error, json_dumps


class TanzaniaBulkBase(IndexSpider):
    # BaseSpider
    default_from_date = '2023-07-30'

    # IndexSpider
    result_count_pointer = '/recordsFilteredCount'
    use_page = True
    start_page = 1
    formatter = None
    limit = 10
    parse_list_callback = 'parse_items'

    # Local
    main_url = 'https://nest.go.tz/gateway/nest-data-portal-api'
    payload = {
        "page": 1,
        "pageSize": 10,
        "fields": [
            {
                "fieldName": "publishedDate",
                "isSortable": True,
                "orderDirection": "DESC"
            }
        ],
        "mustHaveFilters": [
            {
                "fieldName": "periodType",
                "value1": "daily",
                "operation": "EQ"
            }
        ]
    }

    def start_requests(self):
        self.payload["mustHaveFilters"].append(
            {
                "fieldName": "dataType",
                # record or release
                "value1": self.data_type.split("_")[0],
                "operation": "EQ"
            }
        )
        if self.from_date and self.until_date:
            for date_name in ["startDate", "endDate"]:
                self.payload["mustHaveFilters"].append({
                    "fieldName": date_name,
                    "value1": f"{self.from_date.strftime(self.date_format)}T00:00:00",
                    "value2": f"{self.until_date.strftime(self.date_format)}T23:59:59",
                    "operation": "BTN"
                }
                )
        url, kwargs = self.url_builder(1, None, None)
        yield scrapy.Request(url, **kwargs, callback=self.parse_list)

    def url_builder(self, value, data, response):
        self.payload['page'] = value
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json;charset=UTF-8'}
        return f'{self.main_url}/packages?withMetaData=true', {
            'method': 'POST',
            'headers': headers,
            'body': json_dumps(self.payload),
            'meta': {'file_name': f'page-{value}.json'},
        }

    @handle_http_error
    def parse_items(self, response):
        data = response.json()
        for item in data['data']:
            yield self.build_request(f'{self.main_url}/api/packages/download/{item["fileName"]}',
                                     formatter=components(-1))
