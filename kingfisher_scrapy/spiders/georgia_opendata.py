from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class GeorgiaOpenData(BaseSpider):
    name = 'georgia_opendata'
    custom_settings = {
        # This has to download a 400MB file so .....
        'DOWNLOAD_TIMEOUT': 60*20,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='http://opendata.spa.ge/json/allTenders.zip',
            callback=self.parse_zip
        )

    def parse_zip(self, response):
        if response.status == 200:

            # Save original file
            save_file_name = self.get_local_file_path_including_filestore('allTenders.zip')
            with open(save_file_name, "wb") as fp:
                fp.write(response.body)

            # Now extract each file one at a time, save to disk and pass to pipelines for processing
            zip_file = ZipFile(save_file_name)
            for finfo in zip_file.infolist():
                if finfo.filename.endswith('.json'):
                    data = zip_file.open(finfo.filename).read()
                    yield self.save_data_to_disk(
                        data,
                        finfo.filename.replace('/', '-'),
                        data_type='release_package',
                        url=response.request.url
                    )
                    if self.is_sample():
                        return

        else:
            yield {
                'success': False,
                'file_name': 'zip.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
