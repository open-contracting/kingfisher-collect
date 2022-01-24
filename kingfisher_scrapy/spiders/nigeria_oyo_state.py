import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class NigeriaOyoState(SimpleSpider):
    """
    Domain
      Nigeria Oyo State Open Contracting Portal
    """
    name = 'nigeria_oyo_state'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # From https://ocdsoyo.oyostate.gov.ng/projects.php
        yield scrapy.Request('https://ocdsoyo.oyostate.gov.ng/json_formation.php', meta={'file_name': 'all.json'})
