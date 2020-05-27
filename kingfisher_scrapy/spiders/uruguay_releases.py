import hashlib

import scrapy

from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import handle_error


class UruguayReleases(UruguayBase):
    name = 'uruguay_releases'

    @handle_error
    def parse_list(self, response):
        root = response.xpath('//item/link/text()').getall()

        if self.sample:
            root = [root[0]]

        for url in root:
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json',
                      'data_type': 'release_package'}
            )
