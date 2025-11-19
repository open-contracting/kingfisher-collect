"""
This spider raises exceptions in different methods. You can use this to test whether exceptions are logged properly.

.. code-block:: bash

   python -m scrapy crawl error -s SPIDER_MODULES=tests.spiders -a raise_init=True
"""

import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.exceptions import IncoherentConfigurationError, SpiderArgumentError


class Error(BaseSpider):
    name = "error"

    def __init__(
        self,
        *args,
        raise_from_crawler=False,
        raise_init=False,
        raise_start=False,
        raise_parse=False,
        **kwargs,
    ):
        super().__init__(
            *args,
            raise_from_crawler=raise_from_crawler,
            raise_init=raise_init,
            raise_start=raise_start,
            raise_parse=raise_parse,
            **kwargs,
        )

        self.raise_from_crawler = raise_from_crawler
        self.raise_init = raise_init
        self.raise_start = raise_start
        self.raise_parse = raise_parse

        if raise_init:
            raise IncoherentConfigurationError("message")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        if spider.raise_from_crawler:
            raise SpiderArgumentError("message")

        return spider

    async def start(self):
        if self.raise_start:
            raise RuntimeError("message")
        yield scrapy.Request("http://httpstat.us/200")

    def parse(self, response):
        if self.raise_parse:
            raise RuntimeError("message")
