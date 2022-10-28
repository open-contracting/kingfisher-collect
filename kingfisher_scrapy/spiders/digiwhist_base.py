import tarfile
from io import BytesIO

import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.util import browser_user_agent, handle_http_error


class DigiwhistBase(BaseSpider):
    """
    Domain
      Digiwhist
    Bulk download documentation
      https://opentender.eu/download
    """
    user_agent = browser_user_agent  # to avoid HTTP 410 error

    # BaseSpider
    line_delimited = True

    # start_urls must be provided by subclasses.

    def start_requests(self):
        # See scrapy.spiders.Spider.start_requests
        for url in self.start_urls:
            yield scrapy.Request(url, meta={'file_name': 'file.tar.gz'})

    @handle_http_error
    def parse(self, response):

        # Load a line at the time, pass it to API
        with tarfile.open(fileobj=BytesIO(response.body), mode="r:gz") as tar:
            with tar.extractfile(tar.next()) as f:
                yield self.build_file_from_response(data=f, response=response, file_name='data.json',
                                                    data_type='release_package')
