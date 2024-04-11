import json

import pytest

from kingfisher_scrapy.base_spiders import BigFileSpider
from kingfisher_scrapy.exceptions import IncoherentConfigurationError
from kingfisher_scrapy.items import File
from tests import FILE_LENGTH, response_fixture, spider_with_crawler


@pytest.mark.parametrize('data_type', ['release', 'record', None, 'other'])
def test_data_type_invalid(data_type):
    with pytest.raises(IncoherentConfigurationError) as e:
        spider_with_crawler(BigFileSpider, data_type=data_type)
    assert str(e.value) == f"data_type must be 'release_package' or 'record_package', not {data_type!r}."


@pytest.mark.parametrize('data_type', ['release_package', 'record_package'])
def test_data_type_valid(data_type):
    # No IncoherentConfigurationError exception.
    spider_with_crawler(BigFileSpider, data_type=data_type)


@pytest.mark.parametrize('sample,len_items,len_releases,data_type,key', [
    (None, 2, 100, 'release_package', 'releases'),
    (5, 1, 5, 'release_package', 'releases'),
    (5, 1, 5, 'record_package', 'records')
])
def test_parse_package(sample, len_items, len_releases, data_type, key):
    spider = spider_with_crawler(spider_class=BigFileSpider, sample=sample, data_type=data_type)
    package = {key: []}
    for i in range(200):
        package[key].append({'key': 'value'})

    response = response_fixture(body=json.dumps(package).encode(), meta={'file_name': 'test.json'})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item.__dict__) == FILE_LENGTH
    assert item.file_name == 'test.json'
    assert item.url == 'http://example.com'
    assert item.data_type == data_type
    assert item.data['package'] is not None
    assert item.data['data'] is not None

    with pytest.raises(StopIteration):
        next(generator)
