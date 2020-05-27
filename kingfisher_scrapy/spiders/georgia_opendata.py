import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


class GeorgiaOpenData(ZipSpider):
    name = 'georgia_opendata'
    custom_settings = {
        # This has to download a 400MB file so .....
        'DOWNLOAD_TIMEOUT': 60*20,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='http://opendata.spa.ge/json/allTenders.zip'
        )

    @handle_error(file_name='all.json')
    def parse(self, response):
            yield from self.parse_zipfile(response, 'release_package', file_format='release_package')
