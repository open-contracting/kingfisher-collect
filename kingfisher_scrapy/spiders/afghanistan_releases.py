import json

import scrapy


class AfghanistanReleases(scrapy.Spider):
    name = 'afghanistan_releases'
    start_urls = ['https://ocds.ageops.net/api/ocds/releases/dates']
    download_delay = 1

    def parse(self, response):
        urls = json.loads(response.body)

        if hasattr(self, 'sample') and self.sample == 'true':
            # Only get one date
            urls = [urls[0]]

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_release_urls)

    def parse_release_urls(self, response):
        release_urls = json.loads(response.body)

        if len(release_urls) > 0:  # Some dates have no releases
            if hasattr(self, 'sample') and self.sample == 'true':
                # Only get one release
                release_urls = [release_urls[0]]

            for release_url in release_urls:
                yield {
                    "file_urls": [release_url],
                    "data_type": "release"
                }
