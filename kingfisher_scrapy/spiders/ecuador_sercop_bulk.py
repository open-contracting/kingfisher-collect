import ijson

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error


class EcuadorSERCOPBulk(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública (SERCOP)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2015-01'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
        https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api
    Bulk download documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos
    """
    name = 'ecuador_sercop_bulk'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2015-01'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download'\
              '?type=json&year={0.year:d}&month={0.month:02d}&method=all'
    formatter = staticmethod(components(-1))

    def build_request(self, url, formatter, **kwargs):
        meta = {'meta': {'file_name': f'{formatter(url)}.zip'}}
        return super().build_request(url, formatter, **meta)

    @handle_http_error
    def parse(self, response):
        item = next(super().parse(response))
        data = item['data']
        package = {}
        # The file is a JSON array of release packages that we rearrange in a single package to avoid losing data
        # in kingfisher-process-v1
        for number, obj in enumerate(util.transcode(self, ijson.items, data, 'item'), 1):
            if not package:
                package = obj
                package['releases'] = []
            package['releases'].extend(obj['releases'])
            if self.sample and number > self.sample:
                break
        item['data'] = package
        yield item
