import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoAdministracionPublicaFederal(BaseSpider):
    """
    Bulk downloads: https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    """
    name = 'mexico_administracion_publica_federal'

    def start_requests(self):
        yield scrapy.Request(
            url='https://api.datos.gob.mx/v1/contratacionesabiertas',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            data = json.loads(response.text)

            # Actual data
            yield self.save_response_to_disk(
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

        else:
            yield self.build_file_error_from_response(response)
