import logging
import os
from datetime import datetime
from unittest.mock import Mock

import psycopg2
import pytest
from ocdsmerge.exceptions import DuplicateIdValueWarning
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import DatabaseStore, FilesStore
from tests import spider_with_crawler

DATABASE_URL = os.getenv('KINGFISHER_COLLECT_DATABASE_URL')
SKIP_TEST_IF = not DATABASE_URL and ('CI' not in os.environ or 'CI_SKIP' in os.environ)


@pytest.fixture
def cursor():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        yield cursor
    finally:
        cursor.execute('DROP TABLE IF EXISTS test')
        cursor.execute('DROP TABLE IF EXISTS new_name')
        connection.commit()
        cursor.close()
        connection.close()


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00')

    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'DATABASE_URL is not set.'

    spider.crawler.settings = {'DATABASE_URL': 'test', 'FILES_STORE': None}
    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'FILES_STORE is not set.'


@pytest.mark.skipif(SKIP_TEST_IF, reason='KINGFISHER_COLLECT_DATABASE_URL must be set')
@pytest.mark.parametrize('from_date,default_from_date,messages', [
    (None, None, ['Getting the date from which to resume the crawl from the test table']),
    (None, '2020-01-01', ['Getting the date from which to resume the crawl from the test table']),
    ('2020-01-01', None, []),
    ('2020-01-01', '2020-01-01', []),
])
def test_spider_opened_no_resume(cursor, caplog, tmpdir, from_date, default_from_date, messages):
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': DATABASE_URL, 'FILES_STORE': tmpdir})
    spider.from_date = from_date
    spider.default_from_date = default_from_date

    extension = DatabaseStore.from_crawler(spider.crawler)

    with caplog.at_level(logging.INFO):
        extension.spider_opened(spider)

    cursor.execute("SELECT to_regclass('test')")
    table_exists = cursor.fetchone()[0]

    assert table_exists == 'test'
    assert spider.from_date == from_date
    assert [record.message for record in caplog.records] == messages


@pytest.mark.skipif(SKIP_TEST_IF, reason='KINGFISHER_COLLECT_DATABASE_URL must be set')
def test_spider_opened_resume(caplog, tmpdir):
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': DATABASE_URL, 'FILES_STORE': tmpdir})
    spider.data_type = 'release_package'

    extension = DatabaseStore.from_crawler(spider.crawler)

    files_store_extension = FilesStore.from_crawler(spider.crawler)
    response = Mock()
    response.body = b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'
    response.request.meta = {'file_name': 'file.json'}
    item = spider.build_file_from_response(response, file_name='file.json', data_type='release_package')
    files_store_extension.item_scraped(item, spider)

    extension.spider_opened(spider)
    caplog.clear()
    extension.spider_closed(spider, 'finished')

    with caplog.at_level(logging.INFO):
        extension.spider_opened(spider)

    assert spider.from_date == datetime(2021, 5, 26, 0, 0)
    assert [record.message for record in caplog.records] == [
        'Getting the date from which to resume the crawl from the test table',
        'Resuming the crawl from 2021-05-26',
    ]


@pytest.mark.skipif(SKIP_TEST_IF, reason='KINGFISHER_COLLECT_DATABASE_URL must be set')
def test_spider_closed_warnings(caplog, tmpdir):
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': DATABASE_URL, 'FILES_STORE': tmpdir})
    spider.data_type = 'release_package'
    spider.database_store_compile_releases = True

    extension = DatabaseStore.from_crawler(spider.crawler)

    files_store_extension = FilesStore.from_crawler(spider.crawler)

    response = Mock()
    response.body = b'{"releases":[{"ocid":"x","date":"2021-05-26T10:00:00Z","parties":[{"id":"x"},{"id":"x"}]}]}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'
    response.request.meta = {'file_name': 'file.json'}
    item = spider.build_file_from_response(response, file_name='file-x.json', data_type='release_package')
    files_store_extension.item_scraped(item, spider)

    response.body = b'{"releases":[{"ocid":"y","date":"2021-05-26T10:00:00Z","parties":[{"id":"y"}]}]}'
    item = spider.build_file_from_response(response, file_name='file-y.json', data_type='release_package')
    files_store_extension.item_scraped(item, spider)

    response.body = b'{"releases":[{"ocid":"z","date":"2021-05-26T10:00:00Z","parties":[{"id":"z"},{"id":"z"}]}]}'
    item = spider.build_file_from_response(response, file_name='file-z.json', data_type='release_package')
    files_store_extension.item_scraped(item, spider)

    extension.spider_opened(spider)
    caplog.clear()

    with pytest.warns(DuplicateIdValueWarning) as records:
        with caplog.at_level(logging.INFO):
            extension.spider_closed(spider, 'finished')

    assert spider.from_date == datetime(2021, 5, 26, 0, 0)
    assert [record.message for record in caplog.records] == [
        f'Reading the {tmpdir}/test/20210525_000000 crawl directory with the empty prefix',
        'Creating generator of compiled releases',
        f'Writing the JSON data to the {tmpdir}/test/20210525_000000/data.csv CSV file',
        'Replacing the JSON data in the test table',
    ]

    assert [record.message for record in records] == [
        ("x: Multiple objects have the `id` value 'x' in the `parties` array"),
        ("z: Multiple objects have the `id` value 'z' in the `parties` array"),
    ]


@pytest.mark.skipif(SKIP_TEST_IF, reason='KINGFISHER_COLLECT_DATABASE_URL must be set')
@pytest.mark.parametrize('data,data_type,sample,compile_releases,table_name', [
    (b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}', 'release_package', None, False, 'new_name'),
    (b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}', 'release_package', 1, False, None),
    (b'{"releases": [{"ocid":"1", "date": "2021-05-26T10:00:00Z"}]}', 'release_package', None, True, None),
    (b'{"records": [{"compiledRelease": {"date": "2021-05-26T10:00:00Z"}}]}', 'record_package', None, False, None),
    (b'{"records": [{"releases": [{"ocid":"1", "date": "2021-05-26T10:00:00Z"}]}]}', 'record_package', None, True,
     None),
])
def test_spider_closed(cursor, caplog, tmpdir, data, data_type, sample, compile_releases, table_name):
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': DATABASE_URL, 'FILES_STORE': tmpdir})
    spider.data_type = data_type
    spider.sample = sample
    spider.database_store_compile_releases = compile_releases
    spider.database_store_table_name = table_name

    expected_table = table_name if table_name else spider.name

    extension = DatabaseStore.from_crawler(spider.crawler)

    files_store_extension = FilesStore.from_crawler(spider.crawler)
    response = Mock()
    response.body = data
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'
    response.request.meta = {'file_name': 'file.json'}
    item = spider.build_file_from_response(response, file_name='file.json', data_type=data_type)
    files_store_extension.item_scraped(item, spider)

    extension.spider_opened(spider)
    caplog.clear()

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'finished')

    cursor.execute(f"SELECT max(data->>'date') FROM {expected_table}")
    max_date = cursor.fetchone()[0]
    assert max_date == '2021-05-26T10:00:00Z'

    if compile_releases:
        if data_type == 'release_package':
            prefix = 'empty'
        else:
            prefix = 'records.item.releases.item'
    elif data_type == 'release_package':
        prefix = 'releases.item'
    else:
        prefix = 'records.item.compiledRelease'

    if sample:
        suffix = '_sample'
    else:
        suffix = ''

    expected_messages = [
        f'Reading the {tmpdir}/test{suffix}/20210525_000000 crawl directory with the {prefix} prefix',
        f'Writing the JSON data to the {tmpdir}/test{suffix}/20210525_000000/data.csv CSV file',
        f'Replacing the JSON data in the {expected_table} table',
    ]
    if compile_releases:
        expected_messages.insert(1, 'Creating generator of compiled releases')
    assert [record.message for record in caplog.records] == expected_messages


@pytest.mark.skipif(SKIP_TEST_IF, reason='KINGFISHER_COLLECT_DATABASE_URL must be set')
def test_spider_closed_error(caplog, tmpdir):
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': DATABASE_URL, 'FILES_STORE': tmpdir})
    extension = DatabaseStore.from_crawler(spider.crawler)

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'closed')

    assert not caplog.records
