import hashlib

import scrapy

from kingfisher_scrapy.spiders.uruguay_base import UruguayBase


class UruguayReleases(UruguayBase):
    """
    API documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    Spider arguments
      sample
        Download only 1 release.
    """
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
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
