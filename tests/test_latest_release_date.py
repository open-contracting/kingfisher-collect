import json

from kingfisher_scrapy.items import File, LatestReleaseDateItem
from kingfisher_scrapy.pipelines import LatestReleaseDate
from tests import spider_with_crawler


def test_process_item():
    spider = spider_with_crawler()
    spider.latest = True
    pipeline = LatestReleaseDate()
    release_package = {"releases": [{"date": "2020-01-01T00:00:00Z"}, {"date": "2020-10-01T00:00:00Z"}]}
    record_package = {"records": [release_package]}
    item = File({
        'file_name': 'test',
        'data': json.dumps(release_package),
        'data_type': 'release_package',
        'url': 'http://test.com',
    })
    expected_item = LatestReleaseDateItem({'date': '2020-10-01T00:00:00Z'})
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'release_list'
    item['data'] = json.dumps(release_package['releases'])
    spider.name = 'test3'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'release_package_list'
    item['data'] = json.dumps([release_package])
    spider.name = 'test4'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'release_package_list_in_results'
    item['data'] = json.dumps({'results': [release_package]})
    spider.name = 'test5'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'release'
    item['data'] = json.dumps(release_package['releases'][1])
    spider.name = 'test6'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'compiled_release'
    spider.name = 'test7'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'record_package'
    item['data'] = json.dumps(record_package)
    spider.name = 'test2'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'record'
    item['data'] = json.dumps(record_package['records'][0])
    spider.name = 'test8'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'record'
    item['data'] = json.dumps({'compiledRelease': release_package['releases'][1]})
    spider.name = 'test-compiledRelease'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'record_list'
    item['data'] = json.dumps([record_package['records'][0]])
    spider.name = 'test9'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'record_package_list'
    item['data'] = json.dumps([record_package])
    spider.name = 'test10'
    assert pipeline.process_item(item, spider) == expected_item

    item['data_type'] = 'record_package_list_in_results'
    item['data'] = json.dumps({'results': [record_package]})
    spider.name = 'test11'
    assert pipeline.process_item(item, spider) == expected_item

    spider.latest = False
    assert pipeline.process_item(item, spider) == item
