import logging
import os
from unittest.mock import Mock

import psycopg2
import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import DatabaseStore, FilesStore
from tests import spider_with_crawler


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00')

    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'DATABASE_URL is not set.'

    spider.crawler.settings = {'DATABASE_URL': 'test', 'FILES_STORE': None}
    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'FILES_STORE is not set.'


@pytest.mark.parametrize('from_date,default_from_date,date_format', [
    (None, None, None),
    ('2020-01-01', None, 'date'),
    ('2020-01-01', '2020-01-01', 'date'),
])
def test_spider_opened_first_time(caplog, tmpdir, from_date, default_from_date, date_format):
    database_url = os.getenv('KINGFISHER_COLLECT_DATABASE_URL')

    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': database_url, 'FILES_STORE': tmpdir})
    spider.from_date = from_date
    spider.default_from_date = default_from_date
    if date_format:
        spider.date_format = spider.VALID_DATE_FORMATS[date_format]
    extension = DatabaseStore.from_crawler(spider.crawler)
    with caplog.at_level(logging.INFO):
        extension.spider_opened(spider)
        if not from_date:
            assert [record.message for record in caplog.records][-5:] == [
                'Getting the date from which to resume the crawl (if any)']

    connection = psycopg2.connect(database_url)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT to_regclass('test');")
        table_exists = cursor.fetchone()[0]
        assert table_exists == 'test'
        assert spider.from_date == from_date

        cursor.execute('DROP TABLE test')
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def test_spider_closed_error(caplog, tmpdir):
    database_url = os.getenv('KINGFISHER_COLLECT_DATABASE_URL')

    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': database_url, 'FILES_STORE': tmpdir})
    extension = DatabaseStore.from_crawler(spider.crawler)

    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, 'closed')

    assert not caplog.records


@pytest.mark.parametrize('data,data_type,sample,compile_releases', [
    (b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}', 'release_package', None, False),
    (b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}', 'release_package', 1, False),
    (b'{"releases": [{"ocid":"1", "date": "2021-05-26T10:00:00Z"}]}', 'release_package', None, True),
    (b'{"records": [{"compiledRelease": {"date": "2021-05-26T10:00:00Z"}}]}', 'record_package', None, False),
])
def test_spider_closed(caplog, tmpdir, data, data_type, sample, compile_releases):
    caplog.set_level(logging.INFO)
    database_url = os.getenv('KINGFISHER_COLLECT_DATABASE_URL')
    expected_date = '2021-05-26T10:00:00Z'

    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00',
                                 settings={'DATABASE_URL': database_url, 'FILES_STORE': tmpdir})

    spider.data_type = data_type
    spider.sample = sample
    spider.compile_releases = compile_releases

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
    extension.spider_closed(spider, 'finished')

    connection = psycopg2.connect(database_url)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT max(data->>'date') FROM test")
        max_date = cursor.fetchone()[0]
        assert max_date == expected_date

        cursor.execute('DROP TABLE test')
        connection.commit()
        expected_messages = [
                'Reading the crawl directory',
                'Writing the JSON data to a CSV file',
                'Replacing the JSON data in the SQL table',
            ]
        if compile_releases:
            expected_messages.insert(1, 'Creating compiled releases')
        assert [record.message for record in caplog.records][-5:] == expected_messages

    finally:
        cursor.close()
        connection.close()
