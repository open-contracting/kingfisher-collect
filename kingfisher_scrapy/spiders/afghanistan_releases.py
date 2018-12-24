import json

import scrapy


class AfghanistanReleases(scrapy.Spider):
    name = 'afghanistan_releases'
    start_urls = ['https://ocds.ageops.net/api/ocds/releases/dates']
    download_delay = 1

    def parse(self, response):
        for url in json.loads(response.body):
            yield scrapy.Request(url, callback=self.parse_release_urls)

    def parse_release_urls(self, response):
        yield {
            "file_urls": json.loads(response.body),
            "data_type": "release"
        }
