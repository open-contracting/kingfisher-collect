# isort:skip_file
# Avoid circular dependencies at runtime.
# https://github.com/PyCQA/isort#skip-processing-of-imports-outside-of-configuration

from kingfisher_scrapy.base_spiders.base_spider import BaseSpider
from kingfisher_scrapy.base_spiders.compressed_file_spider import CompressedFileSpider
from kingfisher_scrapy.base_spiders.simple_spider import SimpleSpider
from kingfisher_scrapy.base_spiders.big_file_spider import BigFileSpider
from kingfisher_scrapy.base_spiders.index_spider import IndexSpider
from kingfisher_scrapy.base_spiders.links_spider import LinksSpider
from kingfisher_scrapy.base_spiders.periodic_spider import PeriodicSpider

__all__ = (
    "BaseSpider",
    "BigFileSpider",
    "CompressedFileSpider",
    "IndexSpider",
    "LinksSpider",
    "PeriodicSpider",
    "SimpleSpider",
)
