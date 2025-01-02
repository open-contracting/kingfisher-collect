import json

import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import SimpleSpider


class AlbaniaPublicProcurementCommissionBase(SimpleSpider):
    # BaseSpider
    date_format = 'year'
    date_required = True
    root_path = 'result'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        for year in util.date_range_by_year(self.from_date.year, self.until_date.year):
            payload = {
                "extraConditions": [
                    [self.date_param, ">=", f"1/1/{year}"],
                    [self.date_param, "<=", f"1/1/{year + 1}"],
                ]
            }
            yield scrapy.Request(
                self.base_url, meta={'file_name': f'{year}.json'}, method='POST', body=json.dumps(payload),
                headers={'Accept': 'application/json', 'Content-Type': 'application/json'}
            )
