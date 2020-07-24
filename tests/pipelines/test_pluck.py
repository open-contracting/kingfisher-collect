import json

import pytest
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileError, PluckedItem
from kingfisher_scrapy.pipelines import Pluck
from tests import spider_with_crawler

release_package = {"releases": [{"date": "2020-01-01T00:00:00Z"}, {"date": "2020-10-01T00:00:00Z"}]}
record_package = {"records": [release_package]}
parameters = [
    # Releases
    ('release_package', release_package),
    ('release_package_list', [release_package]),
    ('release_package_list_in_results', {'results': [release_package]}),
    ('release', release_package['releases'][1]),
    ('compiled_release', release_package['releases'][1]),
    # Records
    ('record_package', record_package),
    ('record_package_list', [record_package]),
    ('record_package_list_in_results', {'results': [record_package]}),
    ('record', record_package['records'][0]),
    ('record', {'compiledRelease': release_package['releases'][1]}),
]


@pytest.mark.parametrize('data_type,data', parameters)
def test_disabled(data_type, data):
    spider = spider_with_crawler()

    pipeline = Pluck()
    item = File({
        'file_name': 'test',
        'data': json.dumps(data),
        'data_type': data_type,
        'url': 'http://test.com',
    })

    assert pipeline.process_item(item, spider) == item


@pytest.mark.parametrize('data_type,data', parameters)
def test_process_item(data_type, data):
    spider = spider_with_crawler(release_pointer='/date', truncate=10)

    pipeline = Pluck()
    item = File({
        'file_name': 'test',
        'data': json.dumps(data),
        'data_type': data_type,
        'url': 'http://test.com',
    })

    assert pipeline.process_item(item, spider) == PluckedItem({'value': '2020-10-01'})


def test_process_item_file_error():
    spider = spider_with_crawler(release_pointer='/date', truncate=10)

    pipeline = Pluck()
    item = FileError({
        'file_name': 'test',
        'url': 'http://test.com',
        'errors': 'error',
    })

    with pytest.raises(DropItem):
        pipeline.process_item(item, spider)
