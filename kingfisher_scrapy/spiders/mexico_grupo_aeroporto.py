import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoGrupoAeroporto(BaseSpider):
    name = 'mexico_grupo_aeroporto'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='http://gacmda.gacm.mx:8880/files/opendata/coleccion/concentrado05032019RELEASE.json',
            meta={'kf_filename': 'concentrado05032019RELEASE.json'}
        )

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type='release_package')

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
