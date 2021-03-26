from operator import itemgetter
from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase
from kingfisher_scrapy.util import components, handle_http_error


class NigeriaBudeshiRecords(NigeriaBudeshiBase):
    """
    Domain
      Budeshi Nigeria
    API documentation
      https://budeshi.ng/Api
    """
    name = 'nigeria_budeshi_records'

    # SimpleSpider
    data_type = 'record_package'

    url = 'https://budeshi.ng/api/record/{}'

    @handle_http_error
    def parse_list(self, response):
        project_list = response.json()
        for project in sorted(project_list, key=itemgetter('year'), reverse=True):
            yield self.build_request(self.url.format(project['id']), formatter=components(-2))
