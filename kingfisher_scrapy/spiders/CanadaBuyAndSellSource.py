import scrapy


class CanadaBuyAndSellSource(scrapy.Spider):
    name = "canada_buyandsell"

    def start_requests(self):
        urls = [
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
        ]
        if hasattr(self, 'sample') and self.sample == 'true':
            urls = [
                'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            ]
        for index, url in enumerate(urls):
            yield scrapy.Request(url, meta={'filename': str(index) + '.json', 'data_type': 'release_package'})

    def parse(self, response):
        filename = response.meta['filename']
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
