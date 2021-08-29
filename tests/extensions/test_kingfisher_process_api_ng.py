import os
from unittest.mock import MagicMock

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import FilesStore, KingfisherProcessAPI2
from tests import spider_with_crawler, spider_with_files_store


class Response(object):
    def json(self):
        return self.json_response


def test_from_crawler():
    spider = spider_with_crawler(settings={
        'KINGFISHER_API2_URL': 'http://httpbin.org/anything',
        'KINGFISHER_API2_USERNAME': 'xxx',
        'KINGFISHER_API2_PASSWORD': 'password',
    })

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert extension.username == 'xxx'
    assert extension.password == 'password'
    assert extension.url == 'http://httpbin.org/anything'


def test_from_crawler_missing_uri():
    spider = spider_with_crawler(settings={
        "KINGFISHER_API_URL": "missing",
        "KINGFISHER_API2_USERNAME": "aaa",
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert str(excinfo.value) == "KINGFISHER_API2_URL is not set."


def test_from_crawler_missing_password():
    spider = spider_with_crawler(settings={
        "KINGFISHER_API2_URL": "/some/uti",
        "KINGFISHER_API2_USERNAME": "aaa",
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert str(excinfo.value) == "Both KINGFISHER_API2_USERNAME and KINGFISHER_API2_PASSWORD must be set."


def mocked_spider_open(cls, *args, **kwargs):
    # Your custom testing override
    return 1


def test_spider_opened(tmpdir):
    spider = spider_with_files_store(tmpdir, settings={
        'KINGFISHER_API2_URL': 'anything',
        'KINGFISHER_API2_USERNAME': 'xxx',
        'KINGFISHER_API2_PASSWORD': 'password',
    })

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    response = Response()
    response.ok = True
    response.json_response = {"collection_id": "1"}
    extension._post_sync = MagicMock(return_value=response)
    extension.spider_opened(spider)

    extension._post_sync.assert_called_with('api/v1/create_collection',
                                            {
                                                'source_id': 'test',
                                                'data_version': '2001-02-03 04:05:06',
                                                'note': None,
                                                'sample': None,
                                                'compile': True,
                                                'upgrade': False,
                                                'check': True
                                            })


def test_spider_closed(tmpdir):
    spider = spider_with_files_store(tmpdir, settings={
        'KINGFISHER_API2_URL': 'anything',
        'KINGFISHER_API2_USERNAME': 'xxx',
        'KINGFISHER_API2_PASSWORD': 'password',
    })

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    response = Response()
    response.ok = True
    response.json_response = '{"collection_id":"1"}'

    extension._post_sync = MagicMock(return_value=response)
    extension.spider_closed(spider, "done")

    call_args = extension._post_sync.call_args
    call = call_args[0]

    assert call[0] == "api/v1/close_collection"
    assert call[1] == {
                        'collection_id': 1,
                        'reason': 'done',
                        'stats': {
                            'kingfisher_process_items_failed_post': 0,
                            'kingfisher_process_items_sent_post': 0,
                            'kingfisher_process_items_sent_rabbit': 0,
                            'kingfisher_process_items_failed_rabbit': 0,
                            'start_time': '2001-02-03 04:05:06'
                        }}


def test_item_scraped(tmpdir):
    settings = {
        "KINGFISHER_API_LOCAL_DIRECTORY": str(tmpdir.join('xxx')),
        'KINGFISHER_API2_URL': 'anything',
        'KINGFISHER_API2_USERNAME': 'xxx',
        'KINGFISHER_API2_PASSWORD': 'password',
    }

    spider = spider_with_files_store(tmpdir, settings=settings)
    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    item = spider.build_file(
        file_name='file.json',
        url='https://example.com/remote.json',
        data=b'{"key": "value"}',
        data_type='release_package',
    )

    store_extension = FilesStore.from_crawler(spider.crawler)
    store_extension.item_scraped(item, spider)

    response = Response()
    response.ok = True
    response.json_response = '{"collection_id":"1"}'

    extension._post_sync = MagicMock(return_value=response)
    extension.item_scraped(item, spider)

    call_args = extension._post_sync.call_args
    call = call_args[0]
    assert call[0] == "api/v1/create_collection_file"
    assert call[1] == {
                        'collection_id': 1,
                        'path': os.path.join(item['files_store'], item['path']),
                        'url': 'https://example.com/remote.json'}


def test_item_scraped_rabbit(tmpdir):
    settings = {
        "KINGFISHER_API_LOCAL_DIRECTORY": str(tmpdir.join("xxx")),
        "KINGFISHER_API2_URL": "anything",
        "KINGFISHER_API2_USERNAME": "xxx",
        "KINGFISHER_API2_PASSWORD": "password",
        "RABBIT_HOST": "xxx",
        "RABBIT_PORT": "xxx",
        "RABBIT_USERNAME": "xxx",
        "RABBIT_PASSWORD": "xxx",
        "RABBIT_EXCHANGE_NAME": "xxx",
        "RABBIT_PUBLISH_KEY": "xxx",
    }

    spider = spider_with_files_store(tmpdir, settings=settings)
    KingfisherProcessAPI2._get_rabbit_channel = MagicMock(return_value=None)
    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    item = spider.build_file(
        file_name='file.json',
        url='https://example.com/remote.json',
        data=b'{"key": "value"}',
        data_type='release_package',
    )

    store_extension = FilesStore.from_crawler(spider.crawler)
    store_extension.item_scraped(item, spider)

    response = Response()
    response.ok = True
    response.json_response = '{"collection_id":"1"}'

    extension._publish_to_rabbit = MagicMock(return_value=response)
    extension.item_scraped(item, spider)

    call_args = extension._publish_to_rabbit.call_args
    call = call_args[0]
    assert call[0] == {
                        'collection_id': 1,
                        'path': os.path.join(item['files_store'], item['path']),
                        'url': 'https://example.com/remote.json'}
