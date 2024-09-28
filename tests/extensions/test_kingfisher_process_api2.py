import json
import logging
import os
import time
from datetime import datetime, timezone
from unittest.mock import patch
from urllib.parse import urlsplit

import pika
import pytest
import pytest_twisted
from scrapy.crawler import CrawlerRunner
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.extensions import KingfisherProcessAPI2
from kingfisher_scrapy.items import File, FileError, FileItem, PluckedItem
from tests import spider_with_crawler

KINGFISHER_API2_URL = os.getenv('KINGFISHER_API2_TEST_URL', 'http://httpbingo.org/anything/')
RABBIT_URL = os.getenv('RABBIT_URL')
RABBIT_EXCHANGE_NAME = 'kingfisher_process_test'
RABBIT_ROUTING_KEY = 'kingfisher_process_test_api'
RABBIT_QUEUE_NAME = 'kingfisher_process_test_api_loader'
START_URL = urlsplit(KINGFISHER_API2_URL)._replace(path='/get/').geturl()
SETTINGS = {
    'HTTPERROR_ALLOW_ALL': True,
    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    'EXTENSIONS': {
        'kingfisher_scrapy.extensions.FilesStore': 100,
        'kingfisher_scrapy.extensions.KingfisherProcessAPI2': 500,
    },
    # KingfisherProcessAPI2 extension.
    'KINGFISHER_API2_URL': KINGFISHER_API2_URL,
    'RABBIT_URL': RABBIT_URL,
    'RABBIT_EXCHANGE_NAME': RABBIT_EXCHANGE_NAME,
    'RABBIT_ROUTING_KEY': RABBIT_ROUTING_KEY,
}
SKIP_TEST_IF = not RABBIT_URL and ('CI' not in os.environ or 'CI_SKIP' in os.environ)


@pytest.fixture
def channel():
    connection = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=RABBIT_EXCHANGE_NAME, exchange_type='direct', durable=True)
    channel.queue_declare(queue=RABBIT_QUEUE_NAME, durable=False)
    channel.queue_bind(queue=RABBIT_QUEUE_NAME, exchange=RABBIT_EXCHANGE_NAME, routing_key=RABBIT_ROUTING_KEY)
    yield channel
    connection.close()


@pytest.fixture
def item_file():
    return File(
        file_name='file.json',
        url='https://example.com/remote.json',
        data_type='release_package',
        data=b'{"key": "value"}',
    )


class Spider(BaseSpider):
    name = 'test'

    def __init__(self, start_urls=(), item=None, job=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.item = item
        if job:
            self._job = job

    def parse(self, response):
        yield self.item


class Response:
    def __init__(self, status_code=200, content=None):
        self.status_code = status_code
        self.content = content

    @property
    def ok(self):
        return not (400 <= self.status_code < 600)

    def json(self):
        return self.content

    @property
    def text(self):
        return json.dumps(self.content)

    @property
    def headers(self):
        return {}


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
def test_from_crawler():
    spider = spider_with_crawler(settings=SETTINGS)

    extension = KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert extension.url == KINGFISHER_API2_URL
    assert extension.routing_key == RABBIT_ROUTING_KEY
    assert extension.collection_id is None


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler(settings=SETTINGS | {'KINGFISHER_API2_URL': None})

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'KINGFISHER_API2_URL is not set.'


def test_from_crawler_with_database_url():
    spider = spider_with_crawler(settings=SETTINGS | {'DATABASE_URL': 'test'}, crawl_time='2021-05-25T00:00:00')

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI2.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'DATABASE_URL is set.'


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest.mark.parametrize('crawl_time', [None, '2020-01-01T00:00:00'])
@pytest.mark.parametrize(('sample', 'is_sample'), [(None, False), ('true', True)])
@pytest.mark.parametrize('note', [None, 'Started by NAME.'])
@pytest.mark.parametrize('job', [None, '7df53218f37a11eb80dd0c9d92c523cb'])
@pytest.mark.parametrize(('ocds_version', 'upgrade'), [('1.0', True), (None, False)])
@pytest.mark.parametrize(('steps', 'expected_steps'), [
    (None, ['compile']),
    ('compile,check,invalid', ['compile', 'check']),
    ('compile', ['compile']),
    ('check', ['check']),
    ('', []),
])
@pytest.mark.parametrize(('call_count', 'status_code', 'messages'), [
    (2, 200, [
        ('INFO', 'Created collection 1 in Kingfisher Process (DATA_VERSION)'),
        ('INFO', 'Closed collection 1 in Kingfisher Process'),
    ]),
    (1, 500, [
        ('ERROR', 'Failed to create collection: HTTP 500 ({"collection_id": 1}) ({})'),
    ]),
])
@pytest_twisted.inlineCallbacks
def test_spider_opened(
    crawl_time,
    sample,
    is_sample,
    note,
    job,
    ocds_version,
    upgrade,
    steps,
    expected_steps,
    call_count,
    status_code,
    messages,
    tmpdir,
    caplog,
):
    create_response = Response(status_code=status_code, content={'collection_id': 1})
    close_response = Response(status_code=200)
    caplog.set_level(logging.DEBUG)

    with patch.object(
        KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response, close_response]
    ) as mock:
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(
            Spider, job=job, crawl_time=crawl_time, sample=sample, note=note, ocds_version=ocds_version, steps=steps
        )

    expected = {
        'source_id': 'test',
        'sample': is_sample,
        'upgrade': upgrade,
    }

    if note:
        expected['note'] = note
    if job:
        expected['job'] = job

    for step in expected_steps:
        expected[step] = True

    calls = mock.call_args_list

    assert mock.call_count == call_count

    data_version = calls[0].args[2].pop('data_version')
    assert calls[0].args[1:] == ('/api/collections/', expected)

    if crawl_time:
        assert data_version == '2020-01-01 00:00:00'
    else:
        assert data_version.startswith(datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:"))

    if call_count == 2:
        calls[1].args[2].pop('stats')  # pop() ensures its presence
        assert calls[1].args[1:] == ('/api/collections/1/close/', {'reason': 'finished'})

    for levelname, message in [
        (levelname, message.replace('DATA_VERSION', data_version)) for levelname, message in messages
    ]:
        assert any(r.name == 'test' and r.levelname == levelname and r.message == message for r in caplog.records)


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest_twisted.inlineCallbacks
def test_spider_closed_error(tmpdir, caplog):
    # We can't mock disconnect_and_join(), etc. as it must run to isolate tests. That said, if the tests run, then
    # we know the connection is closed and the thread is terminated.

    create_response = Response(status_code=200, content={'collection_id': 1})
    close_response = Response(status_code=500)  # error
    caplog.set_level(logging.DEBUG)

    with patch.object(
        KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response, close_response]
    ) as mock:
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(Spider)

    calls = mock.call_args_list

    assert mock.call_count == 2

    calls[1].args[2].pop('stats')  # pop() ensures its presence
    assert calls[1].args[1:] == ('/api/collections/1/close/', {'reason': 'finished'})

    assert any(
        r.name == 'test' and r.levelname == 'ERROR' and r.message == 'Failed to close collection: HTTP 500 (null) ({})'
        for r in caplog.records
    )


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest_twisted.inlineCallbacks
def test_spider_closed_missing_collection_id(tmpdir):
    create_response = Response(status_code=500)  # error

    with patch.object(KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response]) as mock:
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(Spider)

    mock.assert_called_once()  # only by spider_opened


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest.mark.parametrize('kwargs', [{'package_pointer': '/publishedDate'}, {'keep_collection_open': 'true'}])
@pytest_twisted.inlineCallbacks
def test_spider_closed_return(kwargs, tmpdir):
    create_response = Response(status_code=200, content={'collection_id': 1})

    with patch.object(KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response]) as mock:
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(Spider, **kwargs)

    mock.assert_called_once()  # only by spider_opened


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest.mark.parametrize(('directory', 'filename', 'item'), [
    ('389', 'file.json', File(
        file_name='file.json',
        url='https://example.com',
        data_type='release_package',
        data=b'{"key": "value"}',
    )),
    ('3E7', 'file-1.json', FileItem(
        file_name='file.json',
        url='https://example.com',
        data_type='release_package',
        data=b'{"key": "value"}',
        number=1,
    )),
    ('389', 'file.json', FileError(
        file_name='file.json',
        url='https://example.com',
        errors={'http_code': 500},
    )),
])
@pytest_twisted.inlineCallbacks
def test_item_scraped(directory, filename, item, channel, tmpdir):
    create_response = Response(status_code=200, content={'collection_id': 1})
    close_response = Response(status_code=200)

    # To be sure we consume the expected message, and not an earlier message.
    url = f'https://example.com/remote.{time.time()}.json'
    item.url = url

    with patch.object(KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response, close_response]):
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(Spider, crawl_time='2001-02-03T04:05:06', start_urls=[START_URL], item=item)

    expected = {
        'collection_id': 1,
        'url': url,
    }
    if isinstance(item, FileError):
        expected['errors'] = '{"http_code": 500}'
    else:
        expected['path'] = os.path.join('test', '20010203_040506', directory, filename)

    method_frame, header_frame, body = channel.basic_get(RABBIT_QUEUE_NAME, auto_ack=True)

    assert body is not None  # None if no message in queue
    assert json.loads(body) == expected


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest_twisted.inlineCallbacks
def test_item_scraped_path(item_file, channel, tmpdir):
    create_response = Response(status_code=200, content={'collection_id': 1})
    close_response = Response(status_code=200)

    with (
        tmpdir.as_cwd(),
        patch.object(KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response, close_response]),
    ):
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': 'subdir'})
        yield runner.crawl(Spider, crawl_time='2001-02-03T04:05:06', start_urls=[START_URL], item=item_file)

    method_frame, header_frame, body = channel.basic_get(RABBIT_QUEUE_NAME, auto_ack=True)

    assert body is not None  # None if no message in queue
    assert json.loads(body) == {
        'collection_id': 1,
        'url': 'https://example.com/remote.json',
        'path': 'test/20010203_040506/389/file.json',
    }


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest_twisted.inlineCallbacks
def test_item_scraped_missing_collection_id(item_file, channel, tmpdir):
    create_response = Response(status_code=500)  # error
    close_response = Response(status_code=200)

    with patch.object(KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response, close_response]):
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(Spider, crawl_time='2001-02-03T04:05:06', start_urls=[START_URL], item=item_file)

    assert channel.basic_get(RABBIT_QUEUE_NAME, auto_ack=True) == (None, None, None)


@pytest.mark.skipif(SKIP_TEST_IF, reason='RABBIT_URL must be set')
@pytest_twisted.inlineCallbacks
def test_item_scraped_return(channel, tmpdir):
    create_response = Response(status_code=200, content={'collection_id': 1})
    close_response = Response(status_code=200)
    item_plucked = PluckedItem(value='123')

    with patch.object(KingfisherProcessAPI2, '_post_synchronous', side_effect=[create_response, close_response]):
        runner = CrawlerRunner(settings=SETTINGS | {'FILES_STORE': tmpdir})
        yield runner.crawl(Spider, crawl_time='2001-02-03T04:05:06', start_urls=[START_URL], item=item_plucked)

    assert channel.basic_get(RABBIT_QUEUE_NAME, auto_ack=True) == (None, None, None)
