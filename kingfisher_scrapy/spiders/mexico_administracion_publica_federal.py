import scrapy
import json

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoAdministracionPublicaFederal(BaseSpider):
    """
    Bulk downloads: https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    """
    name = 'mexico_administracion_publica_federal'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://api.datos.gob.mx/v1/contratacionesabiertas',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            data = json.loads(response.body_as_unicode())

            # Actual data
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type="record_package_list_in_results"
            )

            # Load more pages?
            if data['pagination']['page'] == 1 and not self.is_sample():
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
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
