from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase
from kingfisher_scrapy.util import components


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

    def build_urls(self, project):
        yield self.build_request(self.url.format(project['id']), formatter=components(-2))
