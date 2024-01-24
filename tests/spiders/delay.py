"""
This spider has a slow request. You can use this to test integrations (e.g. RabbitMQ restarts).

.. code-block:: bash

   python -m scrapy crawl delay -s SPIDER_MODULES=tests.spiders
"""
import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class Delay(SimpleSpider):
    name = 'delay'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('http://httpbin.org/delay/10', meta={'file_name': 'delay.json'})
