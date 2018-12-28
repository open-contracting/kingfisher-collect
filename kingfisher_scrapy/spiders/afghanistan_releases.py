import json

import scrapy


class AfghanistanReleases(scrapy.Spider):
    name = 'afghanistan_releases'
    start_urls = ['https://ocds.ageops.net/api/ocds/releases/dates']
    download_delay = 1

    def parse(self, response):
        urls = json.loads(response.body)
        print(urls)

        if self.sample:
            urls = [urls[0]]

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_release_urls)

    def parse_release_urls(self, response):
        release_urls = json.loads(response.body)
        if(len(release_urls) > 0):
            yield {
                "file_urls": release_urls,
                "data_type": "release"
            }
