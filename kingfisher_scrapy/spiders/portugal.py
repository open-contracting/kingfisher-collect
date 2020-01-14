import hashlib
import json
from io import BytesIO
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Portugal(BaseSpider):
    name = 'portugal'
    download_warnsize = 0
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        url = 'https://dados.gov.pt/pt/datasets/r/ae76989b-d413-4f00-b1f0-0de1782212b6'
        yield scrapy.Request(
            url,
            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
        )

    def parse(self, response):
        if response.status == 200:
            zip_file = ZipFile(BytesIO(response.body))
            for finfo in zip_file.infolist():
                data = zip_file.open(finfo.filename).read()
                yield self.save_data_to_disk(
                    data,
                    response.request.meta['kf_filename'],
                    data_type='record_package_json_lines',
                    url=response.request.url
                )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
