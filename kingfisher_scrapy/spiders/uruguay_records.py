import hashlib

import scrapy

from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import handle_error


class UruguayRecords(UruguayBase):
    name = 'uruguay_records'
    data_type = 'record_package'

    @handle_error
    def parse_list(self, response):
        base_record_url = 'https://www.comprasestatales.gub.uy/ocds/record/{}'
        root = response.xpath('//item/title/text()').getall()

        if self.sample:
            root = [root[0]]

        for id_compra in root:
            url = base_record_url.format(id_compra.split(',')[0].replace('id_compra:', ''))
            yield scrapy.Request(url, meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})
