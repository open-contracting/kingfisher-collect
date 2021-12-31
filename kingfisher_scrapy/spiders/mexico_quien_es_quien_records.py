from json import dumps

from kingfisher_scrapy.spiders.mexico_quien_es_quien_base import MexicoQuienEsQuienBase
from kingfisher_scrapy.util import handle_http_error


class MexicoQuienEsQuienRecords(MexicoQuienEsQuienBase):
    """
    Domain
      QuiénEsQuién.Wiki
    API documentation
      https://qqwapi-elastic.readthedocs.io/es/latest/
    Swagger API documentation
      https://api.quienesquien.wiki/v3/docs/
    """
    name = 'mexico_quien_es_quien_records'

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    base_url = 'https://api.quienesquien.wiki/v3/record'

    @handle_http_error
    def parse(self, response):
        data = response.json()

        if 'records' in data['data'][0]:
            data['data'][0] = data['data'][0]['records']
            response = response.replace(body=dumps(data))
        yield self.build_file_from_response(response, data_type=self.data_type)
