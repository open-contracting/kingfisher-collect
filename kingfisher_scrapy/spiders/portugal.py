import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class Portugal(ZipSpider):
    """
    API documentation
        https://dados.gov.pt/pt/apidoc/
    Spider arguments
      sample
        Download only the first file in the dataset.
    """
    name = 'portugal'
    data_type = 'record_package'
    encoding = 'iso-8859-1'
    zip_file_format = 'json_lines'

    download_warnsize = 0
    download_timeout = 9999

    def start_requests(self):
        url = 'https://dados.gov.pt/api/1/datasets/?q=ocds&organization={}&page_size={}'
        id = '5ae97fa2c8d8c915d5faa3bf'
        page_size = 20
        yield scrapy.Request(
            url.format(id, page_size),
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        datas = json.loads(response.text)
        for data in datas['data']:
            for resource in data['resources']:
                description = resource['description']
                url = resource['url']
                if description.count("OCDS") or description.count("ocds"):
                    yield scrapy.Request(
                        url,
                        meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                    )
                    if self.sample:
                        break
