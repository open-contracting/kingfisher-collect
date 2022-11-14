import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class NigeriaEdoState(SimpleSpider):
    """
    Domain
      Edo State Open Contracting Data Standards Portal
    Bulk download documentation
      http://edpms.edostate.gov.ng/ocds/
    """
    name = 'nigeria_edo_state'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        url = 'https://edoocds.cloudware.ng/edo-ocds.json'
        yield scrapy.Request(url, meta={'file_name': 'all.json'})
