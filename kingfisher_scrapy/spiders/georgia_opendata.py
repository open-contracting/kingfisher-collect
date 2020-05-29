import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


class GeorgiaOpenData(ZipSpider):
    name = 'georgia_opendata'
    custom_settings = {
        # This has to download a 400MB file so .....
        'DOWNLOAD_TIMEOUT': 60 * 20,
    }

    parse_zipfile_kwargs = {'data_type': 'release_package', 'file_format': 'release_package'}

    def start_requests(self):
        yield scrapy.Request(
            url='http://opendata.spa.ge/json/allTenders.zip',
            meta={'kf_filename': 'all.json'}
        )
