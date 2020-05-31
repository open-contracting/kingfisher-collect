import datetime
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class ChileCompraBaseSpider(BaseSpider):
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }
    download_timeout = 300
    limit = 100
    base_list_url = 'https://apis.mercadopublico.cl/OCDS/data/listaA%C3%B1oMes/{}/{:02d}/{}/{}'
    record_url = 'https://apis.mercadopublico.cl/OCDS/data/record/%s'
    start_year = 2008

    def get_year_month_until(self):
        until_year = datetime.datetime.now().year + 1
        until_month = datetime.datetime.now().month
        if hasattr(self, 'year'):
            self.start_year = int(self.year)
            until_year = self.start_year + 1
            until_month = 12 if self.start_year != datetime.datetime.now().year else until_month
        return until_year, until_month

    def start_requests(self):
        if self.sample:
            yield scrapy.Request(
                self.base_list_url.format(2017, 10, 0, 10),
                meta={'kf_filename': 'list-2017-10.json', 'year': 2017, 'month': 10},
            )
            return

        until_year, until_month = self.get_year_month_until()
        for year in range(self.start_year, until_year):
            for month in range(1, 13):
                # just scrape until the current month when the until year = current year
                if (until_year - 1) == year and month > until_month:
                    break
                yield scrapy.Request(
                    self.base_list_url.format(year, month, 0, self.limit),
                    meta={'kf_filename': 'list-{}-{:02d}.json'.format(year, month), 'year': year, 'month': month},
                )

    @handle_error
    def parse(self, response):
        data = json.loads(response.text)
        if 'data' in data:
            for data_item in data['data']:
                if self.data_type == 'record_package':
                    yield scrapy.Request(
                        self.record_url % data_item['ocid'].replace('ocds-70d2nz-', ''),
                        meta={'kf_filename': 'data-%s-%s.json' % (data_item['ocid'], self.data_type)}
                    )
                else:
                    # the data comes in this format:
                    # "data": [
                    #       {
                    #        "ocid": "",
                    #        "urlTender": "..",
                    #        "urlAward": ".."
                    #        }
                    #    ]
                    for stage in list(data_item.keys()):
                        if 'url' in stage:
                            name = stage.replace('url', '')
                            yield scrapy.Request(
                                data_item[stage],
                                meta={'kf_filename': 'data-%s-%s.json' % (data_item['ocid'], name)}
                            )
            if 'pagination' in data and (data['pagination']['offset'] + self.limit) < data['pagination']['total']:
                year = response.request.meta['year']
                month = response.request.meta['month']
                offset = data['pagination']['offset']
                yield scrapy.Request(
                    self.base_list_url.format(year, month, self.limit + offset, self.limit),
                    meta={'year': year, 'month': month}
                )
        elif 'status' in data and data['status'] != 200:
            yield self.build_file_error_from_response(response, errors={'http_code': data['status']})
        else:
            yield self.build_file_from_response(response, data_type=self.data_type)
