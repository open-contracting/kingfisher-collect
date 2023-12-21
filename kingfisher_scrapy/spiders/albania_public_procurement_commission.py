import json

import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import SimpleSpider


class AlbaniaPublicProcurementCommission(SimpleSpider):
    """
    Domain
      Albania Public Procurement Commission (KPP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2021'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.

    Bulk download documentation
      https://kpp.al/en/Historiku?nrVendimi=&OperatoriEkonmik=&idOperatori=&autoritetiKotraktues=&id=
    """
    name = 'albania_public_procurement_commission'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2021'
    date_required = True
    root_path = 'result'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://kpp.al/api/public/Decision/getBulkJsonByYear'
        for year in util.date_range_by_year(self.from_date.year, self.until_date.year):
            payload = {
                "extraConditions": [
                               ["decision_date", ">=", f"1/1/{year}"],
                               ["decision_date", "<=", f"1/1/{year+1}"]
                           ]
            }
            yield scrapy.Request(url, meta={'file_name': f'{year}.json'}, method='POST', body=json.dumps(payload),
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
