import json
import os
from unittest.mock import patch

import psycopg2
import pytest
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.commands.incrementaldatastore import IncrementalDataStore


# tests/extensions/test_kingfisher_process_api.py fails if execute() is already called.
@pytest.mark.order(-1)
def test_command_without_arguments(capsys):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'incrementaldatastore'])

    actual = capsys.readouterr().err.rsplit("\n", 2)[-2]

    assert actual == "pytest: error: The spider, database-schema and crawl-time arguments must be set."


@pytest.mark.order(-1)
def test_invalid_spider(capsys):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'incrementaldatastore', 'nonexistent', 'test', 'test'])

    actual = capsys.readouterr().err.rsplit("\n", 2)[-2]

    assert actual == "pytest: error: The spider argument 'nonexistent' is not a known spider."


@pytest.mark.order(-1)
def test_invalid_crawl_time(capsys):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'incrementaldatastore', 'fail', 'test', 'test'])

    actual = capsys.readouterr().err.rsplit("\n", 2)[-2]

    assert actual == "pytest: error: The crawl-time argument 'test' must be in YYYY-MM-DDTHH:MM:SS format: time " \
                     "data 'test' does not match format '%Y-%m-%dT%H:%M:%S'"


def test_format_date():
    command = IncrementalDataStore()

    assert command.format_from_date('2020-01-01T00:00:00', 'datetime') == '2020-01-01T00:00:00'
    assert command.format_from_date('2020-01-01T00:00:00', 'date') == '2020-01-01'
    assert command.format_from_date('2020-01-01T00:00:00', 'year-month') == '2020-01'
    assert command.format_from_date('2020-01-01T00:00:00', 'year') == '2020'


@patch('scrapy.crawler.CrawlerProcess.crawl')
@pytest.mark.order(-1)
def test_command(crawl, caplog, tmp_path):
    data_directory = tmp_path / 'fail' / '20200101_000000'
    data_directory.mkdir(parents=True)

    with (data_directory /  'data.json').open('w') as f:
        json.dump({'releases': [{'date': '2020-05-13T00:00:00Z'}]}, f)

    connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
    cursor = connection.cursor()

    try:
        settings = get_project_settings()
        settings['FILES_STORE'] = str(tmp_path)

        with pytest.raises(SystemExit):
            execute(['scrapy', 'incrementaldatastore', 'fail', 'public', '2020-01-01T00:00:00'], settings=settings)

        cursor.execute("SELECT max(data->>'date') FROM fail")
        max_date = cursor.fetchone()[0]

        assert max_date == '2020-05-13T00:00:00Z'

        assert [record.message for record in caplog.records][-5:] == [
            'Getting the date from which to resume the crawl (if any)',
            'Running: scrapy crawl fail -a crawl_time=2020-01-01T00:00:00 -a from_date=2020-05-13',
            'Reading the crawl directory',
            'Writing the JSON data to a CSV file',
            'Replacing the JSON data in the SQL table',
        ]
    finally:
        connection.rollback()
        cursor.close()
        connection.close()
