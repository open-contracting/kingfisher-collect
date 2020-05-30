import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import handle_error


class Armenia(LinksSpider):
    name = 'armenia'
    data_type = 'release_package'
    next_pointer = '/next_page/uri'

    def start_requests(self):
        yield scrapy.Request('https://armeps.am/ocds/release', meta={'kf_filename': 'page1.json'})
