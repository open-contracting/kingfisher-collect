import json
import logging
import os
import time
from unittest.mock import MagicMock

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import FilesStore, KingfisherProcessAPI2
from kingfisher_scrapy.items import FileError, FileItem, PluckedItem
from tests import ExpectedError, spider_with_crawler, spider_with_files_store

rabbit_url = os.getenv('RABBIT_URL')

items_scraped = [
    ('build_file', 'file.json', {
        'file_name': 'file.json',
        'url': 'https://example.com/remote.json',
        'data': b'{"key": "value"}',
        'data_type': 'release_package',
    }),
    (FileItem, 'file-1.json', {
        'number': 1,
        'file_name': 'file.json',
        'url': 'https://example.com/remote.json',
        'data': b'{"key": "value"}',
        'data_type': 'release_package',
    }),
    (FileError, 'file.json', {
        'file_name': 'file.json',
        'url': 'https://example.com/remote.json',
        'errors': {'http_code': 500},
    }),
]


class Response():
    def __init__(self, status_code=200, content=None):
        self.status_code = status_code
        self.content = content

    @property
    def ok(self):
        return not(400 <= self.status_code < 600)

    def json(self):
        return self.content


@pytest.mark.skipif(not rabbit_url and not os.getenv('CI'), reason='RABBIT_URL must be set')
@pytest.mark.parametrize('url,expected,boolean', [
    (rabbit_url, f'{rabbit_url}?blocked_connection_timeout=1800&heartbeat=0', True),
    ('', None, False),
])
def test_from_crawler(url, expected, boolean):
    spider = spider_with_crawler(settings={
        'KINGFISHER_API2_URL': 'http://httpbin.org/anything/',
        'RABBIT_URL': url,
        'RABBIT_EXCHANGE_NAME': 'kingfisher_process_test_1.0',
        'RABBIT_QUEUE_NAME': 'kingfisher_process_test_1.0_api_loader',
        'RABBIT_ROUTING_KEY': 'kingfisher_process_test_1.0_api',
    })

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert extension.rabbit_url == expected
    assert extension.exchange == 'kingfisher_process_test_1.0'
    assert extension.queue == 'kingfisher_process_test_1.0_api_loader'
    assert extension.routing_key == 'kingfisher_process_test_1.0_api'
    assert extension.collection_id is None
    assert bool(extension.channel) is boolean


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler(settings={
        'KINGFISHER_API2_URL': None,
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'KINGFISHER_API2_URL is not set.'


def test_from_crawler_with_database_url():
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00', settings={
        'KINGFISHER_API2_URL': 'http://httpbin.org/anything/',
        'DATABASE_URL': 'test',
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'DATABASE_URL is set.'


@pytest.mark.parametrize('crawl_time', [None, '2020-01-01T00:00:00'])
@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('note', [None, 'Started by NAME.'])
@pytest.mark.parametrize('job', [None, '7df53218f37a11eb80dd0c9d92c523cb'])
@pytest.mark.parametrize('ocds_version,upgrade', [('1.0', True), (None, False)])
@pytest.mark.parametrize('steps', [None, 'compile,check,invalid', 'compile', 'check'])
@pytest.mark.parametrize('status_code,levelname,message', [
    (200, 'INFO', 'Created collection 1 in Kingfisher Process'),
    (500, 'ERROR', 'Failed to create collection. API status code: 500'),
])
def test_spider_opened(crawl_time, sample, is_sample, note, job, ocds_version, upgrade, steps, status_code, levelname,
                       message, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, crawl_time=crawl_time, sample=sample, note=note,
                                     ocds_version=ocds_version, steps=steps)
    if job:
        spider._job = job

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    with caplog.at_level(logging.DEBUG):
        response = Response(status_code=status_code, content={'collection_id': 1})
        extension._post_synchronous = MagicMock(return_value=response)
        extension.spider_opened(spider)

    expected = {
        'source_id': 'test',
        'data_version': '2001-02-03 04:05:06',
        'sample': is_sample,
        'note': note,
        'job': job,
        'upgrade': upgrade,
    }
    if crawl_time:
        expected['data_version'] = '2020-01-01 00:00:00'
    if steps != 'check':
        expected['compile'] = True
    if steps != 'compile':
        expected['check'] = True

    extension._post_synchronous.assert_called_once()
    extension._post_synchronous.assert_called_with(spider, 'api/v1/create_collection', expected)

    assert len(caplog.records) == 1
    assert caplog.records[0].name == 'test'
    assert caplog.records[0].levelname == levelname
    assert caplog.records[0].getMessage() == message


@pytest.mark.parametrize('status_code,levelname,message', [
    (200, 'INFO', 'Closed collection 1 in Kingfisher Process'),
    (500, 'ERROR', 'Failed to close collection. API status code: 500'),
])
def test_spider_closed(status_code, levelname, message, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    with caplog.at_level(logging.DEBUG):
        response = Response(status_code=status_code)
        extension._post_synchronous = MagicMock(return_value=response)
        extension.spider_closed(spider, 'xxx')

    extension._post_synchronous.assert_called_once()
    extension._post_synchronous.assert_called_with(
        spider,
        'api/v1/close_collection',
        {
            'collection_id': 1,
            'reason': 'xxx',
            'stats': {
                'start_time': '2001-02-03 04:05:06',
            },
        }
    )

    assert len(caplog.records) == 1
    assert caplog.records[0].name == 'test'
    assert caplog.records[0].levelname == levelname
    assert caplog.records[0].message == message


@pytest.mark.parametrize('attribute', ['pluck', 'keep_collection_open'])
def test_spider_closed_return(attribute, tmpdir):
    spider = spider_with_files_store(tmpdir)
    setattr(spider, attribute, True)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    extension._post_synchronous = MagicMock(return_value=Response())
    extension.spider_closed(spider, 'xxx')

    extension._post_synchronous.assert_not_called()


def test_spider_closed_missing_collection_id(tmpdir):
    spider = spider_with_files_store(tmpdir)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    extension._post_synchronous = MagicMock(return_value=Response())
    extension.spider_closed(spider, 'xxx')

    extension._post_synchronous.assert_not_called()


@pytest.mark.parametrize('initializer,filename,kwargs', items_scraped)
@pytest.mark.parametrize('status_code,levelname,message,infix', [
    (200, 'DEBUG', 'Created collection file in Kingfisher Process', 'sent'),
    (500, 'ERROR', 'Failed to create collection file. API status code: 500', 'failed'),
])
def test_item_scraped(initializer, filename, kwargs, status_code, levelname, message, infix, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    if isinstance(initializer, str):
        item = getattr(spider, initializer)(**kwargs)
    else:
        item = initializer(**kwargs)

    store_extension = FilesStore.from_crawler(spider.crawler)
    store_extension.item_scraped(item, spider)

    with caplog.at_level(logging.DEBUG):
        response = Response(status_code=status_code)
        extension._post_synchronous = MagicMock(return_value=response)
        extension.item_scraped(item, spider)

    expected = {
        'collection_id': 1,
        'url': 'https://example.com/remote.json',
    }

    if initializer is FileError:
        expected['errors'] = '{"http_code": 500}'
    else:
        expected['path'] = tmpdir.join('test', '20010203_040506', filename)

    extension._post_synchronous.assert_called_once()
    extension._post_synchronous.assert_called_with(spider, 'api/v1/create_collection_file', expected)

    assert extension.stats.get_value(f'kingfisher_process_items_{infix}_post') == 1

    assert len(caplog.records) == 1
    assert caplog.records[0].name == 'test'
    assert caplog.records[0].levelname == levelname
    assert caplog.records[0].message == message


@pytest.mark.parametrize('initializer,filename,kwargs', items_scraped)
@pytest.mark.parametrize('raises,infix', [(False, 'sent'), (True, 'failed')])
def test_item_scraped_rabbit(initializer, filename, kwargs, raises, infix, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, settings={
        'RABBIT_URL': rabbit_url,
        'RABBIT_EXCHANGE_NAME': 'kingfisher_process_test_1.0',
        'RABBIT_QUEUE_NAME': 'kingfisher_process_test_1.0_api_loader',
        'RABBIT_ROUTING_KEY': 'kingfisher_process_test_1.0_api',
    })

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    # To be sure we consume the message we sent.
    kwargs['url'] += str(time.time())

    if isinstance(initializer, str):
        item = getattr(spider, initializer)(**kwargs)
    else:
        item = initializer(**kwargs)

    store_extension = FilesStore.from_crawler(spider.crawler)
    store_extension.item_scraped(item, spider)

    if raises:
        extension._publish_to_rabbit = MagicMock(return_value=Response())
        extension._publish_to_rabbit.side_effect = ExpectedError('message')

    extension.item_scraped(item, spider)

    expected = {
        'collection_id': 1,
        'url': kwargs['url'],
    }

    if initializer is FileError:
        expected['errors'] = '{"http_code": 500}'
    else:
        expected['path'] = tmpdir.join('test', '20010203_040506', filename)

    if raises:
        extension._publish_to_rabbit.assert_called_once()
        extension._publish_to_rabbit.assert_called_with(expected)

    assert extension.stats.get_value(f'kingfisher_process_items_{infix}_rabbit') == 1

    if raises:
        assert len(caplog.records) == 1
        assert caplog.records[0].name == 'test'
        assert caplog.records[0].levelname == 'ERROR'
        assert caplog.records[0].message == 'Failed to publish message to RabbitMQ'
    else:
        method_frame, header_frame, body = extension.channel.basic_get('kingfisher_process_test_1.0_api_loader')
        extension.channel.basic_ack(method_frame.delivery_tag)

        assert len(caplog.records) == 0
        assert json.loads(body) == expected


def test_item_scraped_plucked_item(tmpdir):
    spider = spider_with_files_store(tmpdir)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)
    extension.collection_id = 1

    item = PluckedItem({
        'value': '123',
    })

    extension._post_synchronous = MagicMock(return_value=Response())
    extension.item_scraped(item, spider)

    extension._post_synchronous.assert_not_called()


def test_item_scraped_missing_collection_id(tmpdir):
    spider = spider_with_files_store(tmpdir)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    item = PluckedItem({
        'value': '123',
    })

    extension._post_synchronous = MagicMock(return_value=Response())
    extension.item_scraped(item, spider)

    extension._post_synchronous.assert_not_called()


def test_item_scraped_path(tmpdir):
    with tmpdir.as_cwd():
        spider = spider_with_files_store('subdir')

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

        extension._post_synchronous = MagicMock(return_value=Response())
        extension.item_scraped(item, spider)

        extension._post_synchronous.assert_called_once()
        extension._post_synchronous.assert_called_with(spider, 'api/v1/create_collection_file', {
            'collection_id': 1,
            'url': 'https://example.com/remote.json',
            'path': tmpdir.join('subdir', 'test', '20010203_040506', 'file.json'),
        })
