import tarfile
from io import BytesIO

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_http_error


class DigiwhistBase(BaseSpider):
    """
    Domain
      Digiwhist
    Bulk download documentation
      https://opentender.eu/download
    """
    data_type = 'release_package'
    file_format = 'json_lines'

    def start_requests(self):
        # See scrapy.spiders.Spider.start_requests
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, meta={'file_name': 'file.tar.gz'})

    @handle_http_error
    def parse(self, response):

        # Load a line at the time, pass it to API
        with tarfile.open(fileobj=BytesIO(response.body), mode="r:gz") as tar:
            with tar.extractfile(tar.getnames()[0]) as readfp:
                yield self.build_file_from_response(data=readfp, response=response, file_name='data.json',
                                                    data_type=self.data_type)
