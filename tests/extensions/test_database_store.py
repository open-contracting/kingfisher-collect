import datetime
import logging
import os
from unittest.mock import Mock

import psycopg2
import pytest
from ocdsmerge.exceptions import DuplicateIdValueWarning
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import DatabaseStore, FilesStore
from tests import spider_with_crawler

DATABASE_URL = os.getenv("KINGFISHER_COLLECT_DATABASE_URL")
SKIP_TEST_IF = not DATABASE_URL and ("CI" not in os.environ or "CI_SKIP" in os.environ)


@pytest.fixture
def cursor():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    try:
        yield cursor
    finally:
        cursor.execute("DROP TABLE IF EXISTS test")
        cursor.execute("DROP TABLE IF EXISTS new_name")
        connection.commit()
        cursor.close()
        connection.close()


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler(crawl_time="2021-05-25T00:00:00")

    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == "DATABASE_URL is not set."

    spider.crawler.settings = {"DATABASE_URL": "test", "FILES_STORE": None}
    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == "FILES_STORE is not set."


@pytest.mark.skipif(SKIP_TEST_IF, reason="KINGFISHER_COLLECT_DATABASE_URL must be set")
@pytest.mark.parametrize(
    ("from_date", "default_from_date", "messages"),
    [
        (None, None, ["Getting the date from which to resume the crawl from the test table"]),
        (None, "2020-01-01", ["Getting the date from which to resume the crawl from the test table"]),
        ("2020-01-01", None, ["Starting crawl from 2020-01-01"]),
        ("2020-01-01", "2020-01-01", ["Getting the date from which to resume the crawl from the test table"]),
    ],
)
def test_spider_opened_no_resume(cursor, caplog, tmpdir, from_date, default_from_date, messages):
    spider = spider_with_crawler(
        crawl_time="2021-05-25T00:00:00",
        from_date=from_date,
        default_from_date=default_from_date,
        settings={
            "DATABASE_URL": DATABASE_URL,
            "FILES_STORE": tmpdir,
        },
    )

    extension = DatabaseStore.from_crawler(spider.crawler)

    caplog.clear()
    with caplog.at_level(logging.INFO):
        extension.spider_opened(spider)

    cursor.execute("SELECT to_regclass('test')")
    table_exists = cursor.fetchone()[0]

    assert table_exists == "test"
    if from_date:
        assert spider.from_date == datetime.datetime.strptime(from_date, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc
        )
    else:
        assert spider.from_date == from_date
    assert [record.message for record in caplog.records] == messages


@pytest.mark.skipif(SKIP_TEST_IF, reason="KINGFISHER_COLLECT_DATABASE_URL must be set")
def test_spider_opened_resume(caplog, tmpdir):
    spider = spider_with_crawler(
        crawl_time="2021-05-25T00:00:00",
        settings={
            "DATABASE_URL": DATABASE_URL,
            "FILES_STORE": tmpdir,
        },
    )
    spider.data_type = "release_package"

    extension = DatabaseStore.from_crawler(spider.crawler)

    files_store_extension = FilesStore.from_crawler(spider.crawler)
    response = Mock()
    response.body = b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}'
    response.request = Mock()
    response.request.url = "https://example.com/remote.json"
    response.request.meta = {"file_name": "file.json"}
    item = spider.build_file_from_response(response, file_name="file.json", data_type="release_package")
    files_store_extension.item_scraped(item, spider)

    extension.spider_opened(spider)
    extension.spider_closed(spider, "finished")

    caplog.clear()
    with caplog.at_level(logging.INFO):
        extension.spider_opened(spider)

    assert spider.from_date == datetime.datetime.strptime("2021-05-26T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    assert [record.message for record in caplog.records] == [
        "Getting the date from which to resume the crawl from the test table",
        "Resuming crawl from 2021-05-26",
    ]


@pytest.mark.skipif(SKIP_TEST_IF, reason="KINGFISHER_COLLECT_DATABASE_URL must be set")
def test_spider_closed_warnings(cursor, caplog, tmpdir):
    spider = spider_with_crawler(
        crawl_time="2021-05-25T00:00:00",
        settings={
            "DATABASE_URL": DATABASE_URL,
            "FILES_STORE": tmpdir,
        },
    )
    spider.data_type = "release_package"
    spider.database_store_compile_releases = True

    extension = DatabaseStore.from_crawler(spider.crawler)

    files_store_extension = FilesStore.from_crawler(spider.crawler)

    response = Mock()
    response.body = b'{"releases":[{"ocid":"x","date":"2021-05-26T10:00:00Z","parties":[{"id":"x"},{"id":"x"}]}]}'
    response.request = Mock()
    response.request.url = "https://example.com/remote.json"
    response.request.meta = {"file_name": "file.json"}
    item = spider.build_file_from_response(response, file_name="file-x.json", data_type="release_package")
    files_store_extension.item_scraped(item, spider)

    response.body = b'{"releases":[{"ocid":"y","date":"2021-05-26T10:00:00Z","parties":[{"id":"y"}]}]}'
    item = spider.build_file_from_response(response, file_name="file-y.json", data_type="release_package")
    files_store_extension.item_scraped(item, spider)

    response.body = b'{"releases":[{"ocid":"z","date":"2021-05-26T10:00:00Z","parties":[{"id":"z"},{"id":"z"}]}]}'
    item = spider.build_file_from_response(response, file_name="file-z.json", data_type="release_package")
    files_store_extension.item_scraped(item, spider)

    extension.spider_opened(spider)

    caplog.clear()
    with pytest.warns(DuplicateIdValueWarning) as records, caplog.at_level(logging.INFO):
        extension.spider_closed(spider, "finished")

    cursor.execute("SELECT * FROM test")

    assert cursor.fetchall() == [
        (
            {
                "ocid": "x",
                "id": "x-2021-05-26T10:00:00Z",
                "date": "2021-05-26T10:00:00Z",
                "tag": ["compiled"],
                "parties": [{"id": "x"}],
            },
        ),
        (
            {
                "ocid": "y",
                "id": "y-2021-05-26T10:00:00Z",
                "date": "2021-05-26T10:00:00Z",
                "tag": ["compiled"],
                "parties": [{"id": "y"}],
            },
        ),
        (
            {
                "ocid": "z",
                "id": "z-2021-05-26T10:00:00Z",
                "date": "2021-05-26T10:00:00Z",
                "tag": ["compiled"],
                "parties": [{"id": "z"}],
            },
        ),
    ]
    assert spider.from_date == datetime.datetime.strptime("2021-05-26T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    assert [record.message for record in caplog.records] == [
        f"Reading the {tmpdir}/test/20210525_000000 crawl directory with the empty prefix",
        "Creating generator of compiled releases",
        f"Writing the JSON data to the {tmpdir}/test/20210525_000000/data.jsonl JSONL file",
        "Replacing the JSON data in the test table (3 rows)",
    ]

    assert [str(record.message) for record in records] == [
        ("x: Multiple objects have the `id` value 'x' in the `parties` array"),
        ("z: Multiple objects have the `id` value 'z' in the `parties` array"),
    ]


@pytest.mark.skipif(SKIP_TEST_IF, reason="KINGFISHER_COLLECT_DATABASE_URL must be set")
@pytest.mark.parametrize(
    ("data", "data_type", "sample", "compile_releases", "table_name"),
    [
        (b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}', "release_package", None, False, "new_name"),
        (b'{"releases": [{"date": "2021-05-26T10:00:00Z"}]}', "release_package", 1, False, None),
        (b'{"releases": [{"ocid":"1", "date": "2021-05-26T10:00:00Z"}]}', "release_package", None, True, None),
        (b'{"records": [{"compiledRelease": {"date": "2021-05-26T10:00:00Z"}}]}', "record_package", None, False, None),
        (
            b'{"records": [{"releases": [{"ocid":"1", "date": "2021-05-26T10:00:00Z"}]}]}',
            "record_package",
            None,
            True,
            None,
        ),
    ],
)
def test_spider_closed(cursor, caplog, tmpdir, data, data_type, sample, compile_releases, table_name):
    spider = spider_with_crawler(
        crawl_time="2021-05-25T00:00:00",
        settings={
            "DATABASE_URL": DATABASE_URL,
            "FILES_STORE": tmpdir,
        },
    )
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
    response.request.url = "https://example.com/remote.json"
    response.request.meta = {"file_name": "file.json"}
    item = spider.build_file_from_response(response, file_name="file.json", data_type=data_type)
    files_store_extension.item_scraped(item, spider)

    extension.spider_opened(spider)

    caplog.clear()
    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, "finished")

    cursor.execute(f"SELECT max(data ->> 'date') FROM {expected_table}")
    max_date = cursor.fetchone()[0]
    assert max_date == "2021-05-26T10:00:00Z"

    if compile_releases:
        prefix = "empty" if data_type == "release_package" else "records.item.releases.item"
    elif data_type == "release_package":
        prefix = "releases.item"
    else:
        prefix = "records.item.compiledRelease"

    suffix = "_sample" if sample else ""

    expected_messages = [
        f"Reading the {tmpdir}/test{suffix}/20210525_000000 crawl directory with the {prefix} prefix",
        f"Writing the JSON data to the {tmpdir}/test{suffix}/20210525_000000/data.jsonl JSONL file",
        f"Replacing the JSON data in the {expected_table} table (1 rows)",
    ]

    if compile_releases:
        expected = {"ocid": "1", "id": "1-2021-05-26T10:00:00Z", "date": "2021-05-26T10:00:00Z", "tag": ["compiled"]}
        expected_messages.insert(1, "Creating generator of compiled releases")
    else:
        expected = {"date": "2021-05-26T10:00:00Z"}

    cursor.execute(psycopg2.sql.SQL("SELECT * FROM {table}").format(table=psycopg2.sql.Identifier(expected_table)))

    assert cursor.fetchall() == [(expected,)]
    assert [record.message for record in caplog.records] == expected_messages


@pytest.mark.skipif(SKIP_TEST_IF, reason="KINGFISHER_COLLECT_DATABASE_URL must be set")
def test_spider_closed_error(caplog, tmpdir):
    spider = spider_with_crawler(
        crawl_time="2021-05-25T00:00:00",
        settings={
            "DATABASE_URL": DATABASE_URL,
            "FILES_STORE": tmpdir,
        },
    )
    extension = DatabaseStore.from_crawler(spider.crawler)

    caplog.clear()
    with caplog.at_level(logging.INFO):
        extension.spider_closed(spider, "closed")

    assert not caplog.records
