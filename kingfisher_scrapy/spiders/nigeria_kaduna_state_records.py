from kingfisher_scrapy.spiders.nigeria_kaduna_state_base import NigeriaKadunaStateBase
from kingfisher_scrapy.util import components


class NigeriaKadunaStateRecords(NigeriaKadunaStateBase):
    """
    Domain
        Budeshi Nigeria - Kaduna State
    API documentation
        https://www.budeshi.ng/kadppa/api
    """
    name = 'nigeria_kaduna_state_records'

    # SimpleSpider
    data_type = 'record_package'

    def build_urls(self, id):
        url = f'{self.base_url}record/{id}'
        yield self.build_request(url, formatter=components(-2))
