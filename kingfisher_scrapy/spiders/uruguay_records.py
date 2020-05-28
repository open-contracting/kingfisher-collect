import hashlib

import scrapy

from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import handle_error


class UruguayRecords(UruguayBase):
    """
    API documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    Spider arguments
      sample
        Download only 1 record.
    """
    name = 'uruguay_records'
    base_record_url = 'https://www.comprasestatales.gub.uy/ocds/record/{}'

    @handle_error
    def parse_list(self, response):
        root = response.xpath('//item/title/text()').getall()

        if self.sample:
            root = [root[0]]

        for id_compra in root:
            url = self.get_url_compra(id_compra)
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json',
                      'data_type': 'record_package'}
            )

    def get_url_compra(self, text):
        return self.base_record_url.format(text.split(',')[0].replace('id_compra:', ''))
