import json

import requests
import scrapy


class AfghanistanReleases(scrapy.Spider):
    name = 'afghanistan_releases'
    start_urls = ['https://ocds.ageops.net/api/ocds/releases/dates']
    download_delay = 1

    def parse(self, response):
        for url in json.loads(response.body):

            yield {
                "file_urls": json.loads(requests.get(str(url)).text),
                "data_type": "release"
            }
