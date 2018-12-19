import scrapy


class CanadaBuyAndSell(scrapy.Spider):
    name = "canada_buyandsell"

    def start_requests(self):
        urls = [
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
        ]
        
        if hasattr(self, 'sample') and self.sample == 'true':
            yield scrapy.Request(urls[0])
        else:
            for url in urls:
                yield scrapy.Request(url)

    def parse(self, response):
        yield {
            "file_urls": [response.url], 
            "data_type": "release_package"
        }
