from unittest.mock import AsyncMock

import pytest
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File
from kingfisher_scrapy.pipelines import Sample
from tests import spider_with_crawler


def test_process_file_without_sample():
    spider = spider_with_crawler()
    pipeline = Sample(spider.crawler)
    item = File(
        file_name="test",
        url="http://test.com",
        data_type="release_package",
        data=b"{}",
    )

    assert pipeline.process_item(item) == item


def test_process_file_with_sample():
    spider = spider_with_crawler(sample=1)
    pipeline = Sample(spider.crawler)
    pipeline.crawler.engine.close_spider_async = AsyncMock()
    item = File(
        file_name="test",
        url="http://test.com",
        data_type="release_package",
        data=b"{}",
    )

    assert pipeline.process_item(item) == item
    with pytest.raises(DropItem):
        pipeline.process_item(item)
