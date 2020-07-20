import json

import pytest
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileError, LatestReleaseDateItem
from kingfisher_scrapy.pipelines import LatestReleaseDate
from tests import spider_with_crawler

release_package = {"releases": [{"date": "2020-01-01T00:00:00Z"}, {"date": "2020-10-01T00:00:00Z"}]}
record_package = {"records": [release_package]}


@pytest.mark.parametrize('data_type,data', [
    # Releases
    ('release_package', release_package),
    ('release_package_list', [release_package]),
    ('release_package_list_in_results', {'results': [release_package]}),
    ('release_list', release_package['releases']),
    ('release', release_package['releases'][1]),
    ('compiled_release', release_package['releases'][1]),
    # Records
    ('record_package', record_package),
    ('record_package_list', [record_package]),
    ('record_package_list_in_results', {'results': [record_package]}),
    ('record_list', record_package['records']),
    ('record', record_package['records'][0]),
    ('record', {'compiledRelease': release_package['releases'][1]}),

])
def test_process_item(data_type, data):
    spider = spider_with_crawler()
    spider.latest = True

    pipeline = LatestReleaseDate()
    item = File({
        'file_name': 'test',
        'data': json.dumps(data),
        'data_type': data_type,
        'url': 'http://test.com',
    })

    assert pipeline.process_item(item, spider) == LatestReleaseDateItem({'date': '2020-10-01'})

    spider.latest = False
    spider.name = 'other'

    assert pipeline.process_item(item, spider) == item


def test_file_error():
    spider = spider_with_crawler()
    spider.latest = True

    pipeline = LatestReleaseDate()

    item = FileError({
        'file_name': 'test',
        'url': 'http://test.com',
        'errors': 'error'
    })
    with pytest.raises(DropItem):
        pipeline.process_item(item, spider)
