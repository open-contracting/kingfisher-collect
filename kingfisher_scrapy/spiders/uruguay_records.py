import hashlib

import scrapy

from kingfisher_scrapy.spiders.uruguay_base import UruguayBase


class UruguayRecords(UruguayBase):
    name = 'uruguay_records'
    base_record_url = 'https://www.comprasestatales.gub.uy/ocds/record/{}'

    def parse_list(self, response):
        if response.status == 200:
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

        else:
            yield self.build_file_error_from_response(response)

    def get_url_compra(self, text):
        return self.base_record_url.format(text.split(',')[0].replace('id_compra:', ''))
