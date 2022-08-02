import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class NigeriaPlateauState(SimpleSpider):
    """
    Domain
      Nigeria Plateau State
    Bulk download documentation
      https://plateaustatebpp.com/ocds
    """
    name = 'nigeria_plateau_state'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('https://plateaustatebpp.com/export', meta={'file_name': 'all.json'})
