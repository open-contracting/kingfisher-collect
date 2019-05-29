import json
import time
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class AfghanistanReleases(BaseSpider):
    name = 'afghanistan_releases'
    start_urls = ['https://ocds.ageops.net/api/ocds/releases/dates']
    download_delay = 1
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://ocds.ageops.net/api/ocds/releases/dates',
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:

            files_urls = json.loads(response.body_as_unicode())
            if hasattr(self, 'sample') and self.sample == 'true':
                files_urls = [files_urls[0]]

            for file_url in files_urls:
                yield scrapy.Request(
                    url=file_url,
                    meta={'kf_filename': file_url.split('/')[-1]+'.json'},
                    callback=self.parse_release_list
                )
        else:
            yield {
                'success': False,
                'file_name': 'list.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse_release_list(self, response):
        if response.status == 200:

            files_urls = json.loads(response.body_as_unicode())
            if hasattr(self, 'sample') and self.sample == 'true':
                files_urls = [files_urls[0]]

            for file_url in files_urls:
                yield scrapy.Request(
                    url=file_url,
                    meta={'kf_filename': file_url.split('/')[-1] + '.json'},
                    callback=self.parse_release
                )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse_release(self, response):
        if response.status == 200:

            self.save_response_to_disk(response, response.request.meta['kf_filename'])
            yield {
                'success': True,
                'file_name': response.request.meta['kf_filename'],
                "data_type": "release",
                "url": response.request.url,
            }
        elif response.status == 429:
            self.crawler.engine.pause()
            time.sleep(600)  # 10 minutes
            self.crawler.engine.unpause()
            url = response.request.url
            # This is dangerous as we might get stuck in a loop here if we always get a 429 response. Try this for now.
            yield scrapy.Request(
                url=url,
                meta={'kf_filename': url.split('/')[-1] + '.json'},
                callback=self.parse_record,
                dont_filter=True,
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
