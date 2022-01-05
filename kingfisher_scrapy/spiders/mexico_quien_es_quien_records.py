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

    # BaseSpider
    root_path = None  # The parse method already fixes the output to make it a correct record package

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    base_url = 'https://api.quienesquien.wiki/v3/record'
    limit = 100  # Decrease the limit so the output file is not too big

    @handle_http_error
    def parse(self, response):
        data = response.json()
        # The first entry of the array is a record package with 'records' as an object. The remaining entries
        # are records. We use the package metadata to wrap all the records into a single record package.
        if 'records' in data['data'][0]:
            package = data['data'][0].copy()
            package['uri'] = None
            package['publishedDate'] = None
            package['records'] = [data['data'][0]['records']]
            for record in data['data'][1:]:
                package['records'].append(record)
            response = response.replace(body=dumps(package))
        yield self.build_file_from_response(response, data_type=self.data_type)
