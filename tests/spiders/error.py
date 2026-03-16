"""
This spider raises exceptions in different methods. You can use this to test whether exceptions are logged properly.

.. code-block:: bash

   python -m scrapy crawl error -s SPIDER_MODULES=tests.spiders -a raise_from_crawler=True
   python -m scrapy crawl error -s SPIDER_MODULES=tests.spiders -a raise_init=True
   python -m scrapy crawl error -s SPIDER_MODULES=tests.spiders -a raise_start=True
   python -m scrapy crawl error -s SPIDER_MODULES=tests.spiders -a raise_parse=True
   python -m scrapy crawl error -s SPIDER_MODULES=tests.spiders -a raise_retryable=True
"""

import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.exceptions import IncoherentConfigurationError, RetryableError, SpiderArgumentError


class Error(BaseSpider):
    name = "error"

    def __init__(
        self,
        *args,
        raise_from_crawler=False,
        raise_init=False,
        raise_start=False,
        raise_parse=False,
        raise_retryable=False,
        **kwargs,
    ):
        super().__init__(
            *args,
            raise_from_crawler=raise_from_crawler,
            raise_init=raise_init,
            raise_start=raise_start,
            raise_parse=raise_parse,
            raise_retryable=raise_retryable,
            **kwargs,
        )

        self.raise_from_crawler = raise_from_crawler
        self.raise_init = raise_init
        self.raise_start = raise_start
        self.raise_parse = raise_parse
        self.raise_retryable = raise_retryable

        if raise_init:
            raise IncoherentConfigurationError("__init__")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        if spider.raise_from_crawler:
            raise SpiderArgumentError("from_crawler")

        return spider

    async def start(self):
        if self.raise_start:
            raise RuntimeError("start")
        yield scrapy.Request("https://httpbingo.org/status/200")

    def parse(self, response):
        if self.raise_parse:
            raise RuntimeError("parse")
        if self.raise_retryable:
            raise RetryableError("parse")
