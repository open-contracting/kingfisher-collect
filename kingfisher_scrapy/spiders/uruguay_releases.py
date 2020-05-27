import hashlib

import scrapy

from kingfisher_scrapy.spiders.uruguay_base import UruguayBase


class UruguayReleases(UruguayBase):
    name = 'uruguay_releases'

    def parse_list(self, response):
        if response.status == 200:
            root = response.xpath('//item/link/text()').getall()

            if self.sample:
                root = [root[0]]

            for url in root:
                yield scrapy.Request(
                    url,
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json',
                          'data_type': 'release_package'}
                )

        else:
            yield self.build_file_error_from_response(response)
