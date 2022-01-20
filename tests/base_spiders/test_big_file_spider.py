import json

import pytest

from kingfisher_scrapy.base_spiders.big_file_spider import BigFileSpider
from kingfisher_scrapy.items import File
from tests import response_fixture, spider_with_crawler


@pytest.mark.parametrize('sample,len_items,len_releases', [(None, 2, 100), (5, 1, 5)])
def test_parse_release_package(sample, len_items, len_releases):
    spider = spider_with_crawler(spider_class=BigFileSpider, sample=sample)
    package = {'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'value'})

    response = response_fixture(body=json.dumps(package).encode(), meta={'file_name': 'test.json'})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item) == 4
    assert item['file_name'] == 'test.json'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'release_package'
    assert item['data']['package'] is not None
    assert item['data']['data'] is not None

    with pytest.raises(StopIteration):
        next(generator)
