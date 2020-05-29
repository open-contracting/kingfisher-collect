import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class MexicoAdministracionPublicaFederal(BaseSpider):
    """
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    Spider arguments
      sample
        Download only 100 records.
    """
    name = 'mexico_administracion_publica_federal'

    def start_requests(self):
        yield scrapy.Request(
            url='https://api.datos.gob.mx/v1/contratacionesabiertas',
            meta={'kf_filename': 'page1.json'}
        )

    @handle_error
    def parse(self, response):
        data = json.loads(response.text)

        # Actual data
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type="record_package_list_in_results"
        )

        # Load more pages?
        if data['pagination']['page'] == 1 and not self.sample:
            total = data['pagination']['total']
            page = 1
            limit = data['pagination']['pageSize']
            while ((page - 1) * limit) < total:
                yield scrapy.Request(
                    url='https://api.datos.gob.mx/v1/contratacionesabiertas?page=%d' % page,
                    meta={'kf_filename': 'page' + str(page) + '.json'}
                )
                page += 1
