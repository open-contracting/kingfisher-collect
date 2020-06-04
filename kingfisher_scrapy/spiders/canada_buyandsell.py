from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components


class CanadaBuyAndSell(SimpleSpider):
    name = 'canada_buyandsell'
    data_type = 'release_package'

    def start_requests(self):
        urls = [
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
        ]
        if self.sample:
            urls = [urls[0]]

        for url in urls:
            yield self.build_request(url, formatter=components(-1))
