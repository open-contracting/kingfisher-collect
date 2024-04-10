import json

import pytest

from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.items import File, PluckedItem
from kingfisher_scrapy.pipelines import Pluck
from tests import spider_with_crawler

releases = [
    {"date": "2020-01-01T00:00:00Z"},
    {"date": "2020-10-01T00:00:00Z"},
]
release_package = {
    "publishedDate": "2000-01-01T00:00:00Z",
    "releases": releases,
}
record_package = {
    "publishedDate": "2000-01-01T00:00:00Z",
    "records": [{"releases": releases}],
}
package_parameters = [
    # Releases
    ('release_package', release_package),
    # Records
    ('record_package', record_package),
]
release_parameters = package_parameters + [
    # Releases
    ('release', {'releases': [release_package['releases'][1]]}),
    # Records
    ('record', {'records': [record_package['records'][0]]}),
    ('record', {'records': [{'compiledRelease': release_package['releases'][1]}]}),
]


@pytest.mark.parametrize('data_type,data', release_parameters)
def test_disabled(data_type, data):
    spider = spider_with_crawler()

    pipeline = Pluck()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type=data_type,
        data=json.dumps(data),
    )

    assert pipeline.process_item(item, spider) == item


def test_from_crawler():
    with pytest.raises(SpiderArgumentError) as excinfo:
        spider_with_crawler(release_pointer='/date', package_pointer='/publishedDate')

    assert str(excinfo.value) == 'You cannot specify both package_pointer and release_pointer spider arguments.'


@pytest.mark.parametrize('data_type,data', release_parameters)
def test_process_item_release_pointer(data_type, data):
    spider = spider_with_crawler(release_pointer='/date', truncate=10)

    pipeline = Pluck()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type=data_type,
        data=json.dumps(data).encode(),
    )

    assert pipeline.process_item(item, spider) == PluckedItem(value='2020-10-01')


@pytest.mark.parametrize('data_type,data', package_parameters)
def test_process_item_package_pointer(data_type, data):
    spider = spider_with_crawler(package_pointer='/publishedDate')

    pipeline = Pluck()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type=data_type,
        data=json.dumps(data).encode(),
    )

    assert pipeline.process_item(item, spider) == PluckedItem(value='2000-01-01T00:00:00Z')


@pytest.mark.parametrize('kwargs', [{'release_pointer': '/nonexistent'}, {'package_pointer': '/nonexistent'}])
def test_process_item_nonexistent_pointer(kwargs):
    spider = spider_with_crawler(**kwargs)

    pipeline = Pluck()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data=json.dumps(release_package).encode(),
    )

    assert pipeline.process_item(item, spider) == PluckedItem(value='error: /nonexistent not found')


def test_process_item_non_package_data_type():
    spider = spider_with_crawler(package_pointer='/publishedDate')

    pipeline = Pluck()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release',
        data=json.dumps(releases[0]).encode(),
    )

    assert pipeline.process_item(item, spider) == PluckedItem(value='error: /publishedDate not found')


def test_process_item_incomplete_json():
    spider = spider_with_crawler(package_pointer='/publishedDate')

    pipeline = Pluck()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data=b'{"key": "value"',
    )

    assert pipeline.process_item(item, spider) == PluckedItem(
        value='error: /publishedDate not found within initial bytes'
    )
