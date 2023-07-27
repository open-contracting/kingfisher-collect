import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider, IndexSpider
from kingfisher_scrapy.util import components, handle_http_error


class PeruOSCEBulk(CompressedFileSpider, IndexSpider):
    """
    Domain
      Organismo Supervisor de las Contrataciones del Estado (OSCE)
    API documentation
      https://contratacionesabiertas.osce.gob.pe/api
    Bulk download documentation
      https://contratacionesabiertas.osce.gob.pe/descargas
    """
    name = 'peru_osce_bulk'

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    formatter = staticmethod(components(-1))
    page_count_pointer = '/pagination/num_pages'
    parse_list_callback = 'parse_files_list'

    peru_base_url = 'https://contratacionesabiertas.osce.gob.pe/api/v1/files?page={0}&paginateBy=10&format=json'

    def start_requests(self):
        yield scrapy.Request(self.peru_base_url.format(1),
                             meta={'file_name': 'list.json'}, callback=self.parse_list)

    def pages_url_builder(self, value, data, response):
        return self.peru_base_url.format(value)

    @handle_http_error
    def parse_files_list(self, response):
        for item in response.json()['results']:
            yield scrapy.Request((item['files']['json']), meta={'file_name': 'data.zip'})
