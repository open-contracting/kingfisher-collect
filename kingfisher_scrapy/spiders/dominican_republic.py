import os
import tempfile

import rarfile
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublic(BaseSpider):
    """
    Bulk download documentation
      https://www.dgcp.gob.do/estandar-mundial-ocds/
    Spider arguments
      sample
        Downloads a release package for the oldest year (2018, first link in the downloads page).
    """
    name = 'dominican_republic'
    skip_latest_release_date = "This command doesn't yet support identifying the latest release in a RAR file."

    def start_requests(self):
        yield scrapy.Request(
            'https://www.dgcp.gob.do/estandar-mundial-ocds/',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.css('.fileLink::attr(href)').getall()
        json_urls = list(filter(lambda x: '/JSON_DGCP_' in x, urls))

        if self.sample and len(json_urls) > 0:
            json_urls = [json_urls[0]]

        for url in json_urls:
            if '/JSON_DGCP_' in url:
                yield self.build_request(url, formatter=components(-1))

    @handle_http_error
    def parse(self, response):
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(response.body)
        file.close()
        with rarfile.RarFile(file.name, charset='utf-8') as tmpfile:
            for f in tmpfile.infolist():
                with tmpfile.open(f) as jsonFile:
                    yield self.build_file(file_name=f.filename, url=response.request.url, data=jsonFile.read(),
                                          data_type='release_package')
        os.remove(file.name)
