import scrapy


class CanadaBuyAndSell(scrapy.Spider):
    name = "canada_buyandsell"
    start_urls = ['https://buyandsell.gc.ca']

    def parse(self, response):
        urls = [
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
        ]
        if hasattr(self, 'sample') and self.sample == 'true':
            urls = ['https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json']

        for url in urls:
            yield {
                "file_urls": [url],
                "data_type": "release_package"
            }
