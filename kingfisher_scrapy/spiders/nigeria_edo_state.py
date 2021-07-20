import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider

class NigeriaEdoState(SimpleSpider):
    """
    Domain
      Edo State Open Contracting Portal - Nigeria
    Bulk download documentation
      http://edpms.edostate.gov.ng/ocds/
    """
    name = 'nigeria_edo_state'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'http://edpms.edostate.gov.ng/ocds/bulkjson.php'
        yield scrapy.Request(url, meta={'file_name': 'all.json'})
