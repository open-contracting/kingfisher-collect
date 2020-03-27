import os
import tempfile

import scrapy
import rarfile

from kingfisher_scrapy.base_spider import BaseSpider


class DominicanRepublic(BaseSpider):
    name = 'dominican_republic'

    def start_requests(self):
        yield scrapy.Request('https://www.dgcp.gob.do/estandar-mundial-ocds/',
                             callback=self.parse_main_page)

    def parse_main_page(self, response):
        if response.status == 200:
            urls = response.css('.fileLink::attr(href)').getall()
            json_urls = list(filter(lambda x: '/JSON_DGCP_' in x, urls))

            if self.sample and len(json_urls) > 0:
                json_urls = [json_urls[0]]

            for url in json_urls:
                if '/JSON_DGCP_' in url:
                    yield scrapy.Request('https:' + url)

    def parse(self, response):
        if response.status == 200:
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(response.body)
            file.close()
            with rarfile.RarFile(file.name, charset='utf-8') as tmpfile:
                for f in tmpfile.infolist():
                    with tmpfile.open(f) as jsonFile:
                        yield self.save_data_to_disk(jsonFile.read(), f.filename, data_type='release_package', url=response.request.url)
            os.remove(file.name)
        else:
            filename = response.request.url.split('/')[-1]
            yield {
                'success': False,
                'file_name': filename,
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
