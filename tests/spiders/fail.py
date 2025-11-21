"""
This spider deliberately generates HTTP errors. You can use this to test whether errors are recorded properly.

.. code-block:: bash

   python -m scrapy crawl fail -s SPIDER_MODULES=tests.spiders
"""

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class Fail(SimpleSpider):
    name = "fail"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request("http://httpstat.us/200", meta={"file_name": "http-200.json"})
        yield scrapy.Request("http://httpstat.us/404", meta={"file_name": "http-404.json"})
        yield scrapy.Request("http://httpstat.us/500", meta={"file_name": "http-500.json"})
        yield scrapy.Request("http://httpstat.us/502", meta={"file_name": "http-502.json"})
