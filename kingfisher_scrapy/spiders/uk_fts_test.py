import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class UKFTSTest(LinksSpider):
    """
    Domain
      Find a Tender Service (FTS)
    Caveats
      This spider uses a test service that returns test data. For getting real data see ``uk_fts`` instead.
    """
    name = 'uk_fts_test'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # uk_fts

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('cursor'))

    def start_requests(self):
        # This URL was provided by the publisher and is not the production URL.
        url = 'https://www-preview.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages'
        yield scrapy.Request(url, meta={'file_name': 'start.json'}, headers={'Accept': 'application/json'})
