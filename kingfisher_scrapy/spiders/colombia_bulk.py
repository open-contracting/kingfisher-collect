import codecs
import json
from io import BytesIO
from urllib.parse import urlparse
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ColombiaBulk(BaseSpider):
    name = 'colombia_bulk'
    start_urls = ['https://www.colombiacompra.gov.co/transparencia/datos-json']
    download_warnsize = 0
    download_timeout = 99999

    def parse(self, response):
        if response.status == 200:
            urls = response.css('.enlaces_contenido').css('a::attr(href)').getall()
            urls = [urls[0]] if self.is_sample() else urls
            for url in urls:
                filename = urlparse(url).path.split('/')[-1]
                yield scrapy.Request(url, meta={'kf_filename': filename}, callback=self.parse_items)
        else:
            yield {
                'success': False,
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse_items(self, response):
        if response.status == 200:
            release_list = []
            page = 0
            with ZipFile(BytesIO(response.body)) as zfile:
                for name in zfile.namelist():
                    with zfile.open(name, 'r') as read_file:
                        for line in codecs.iterdecode(read_file, 'iso-8859-1'):
                            release_data = json.loads(line)['Release']
                            release_list.append(release_data)
                            if len(release_list) == 1000:
                                yield self.save_data_to_disk(release_list, '{}-{}'.format(page,
                                                                                          name),
                                                             encoding='iso-8859-1',
                                                             data_type='release_list', url=response.request.url)
                                release_list = []
                                page = page + 1
                        if release_list:
                            yield self.save_data_to_disk(release_list, '{}-{}'.format(page,
                                                                                      name),
                                                         encoding='iso-8859-1',
                                                         data_type='release_list', url=response.request.url)
                    if self.is_sample():
                        break
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
