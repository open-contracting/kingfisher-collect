from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class HondurasONCAE(BaseSpider):
    name = 'honduras_oncae'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    # the files take too long to be downloaded, so we increase the download timeout
    download_timeout = 900

    def start_requests(self):

        urls = [{'url': 'http://181.210.15.175/datosabiertos/HC1/HC1_datos_{}.json',
                 'start_year': 2005, 'name': 'HC1_datos_{}.json'},
                {'url': 'http://181.210.15.175/datosabiertos/DDC/DDC_datos_{}.json',
                 'start_year': 2010, 'name': 'DDC_datos_{}.json'},
                {'url': 'http://181.210.15.175/datosabiertos/CE/CE_datos_{}.json',
                 'start_year': 2014, 'name': 'CE_datos_{}.json'}
                ]

        current_year = datetime.now().year + 1
        for url in urls:
            for year in range(url['start_year'], current_year):
                yield scrapy.Request(
                    url=url['url'].format(year),
                    meta={'kf_filename': url['name'].format(year)}
                )

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type='release_package')

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
