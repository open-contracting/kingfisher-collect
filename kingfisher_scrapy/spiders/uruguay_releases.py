from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import components, handle_error


class UruguayReleases(UruguayBase):
    name = 'uruguay_releases'
    data_type = 'release_package'

    @handle_error
    def parse_list(self, response):
        urls = response.xpath('//item/link/text()').getall()
        if self.sample:
            urls = [urls[0]]

        for url in urls:
            yield self.build_request(url, formatter=components(-1))
