from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components


class CanadaBuyandsell(SimpleSpider):
    """
    Domain
      Public Works and Government Services Canada
    Caveats
      The dataset is a pilot.
    API documentation
      https://buyandsell.gc.ca/procurement-data/open-contracting-data-standard-pilot/download-ocds-pilot-data
    """

    name = 'canada_buyandsell'

    # BaseSpider
    ocds_version = '1.0'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        urls = [
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-12-13.json',
        ]

        for url in urls:
            yield self.build_request(url, formatter=components(-1))
