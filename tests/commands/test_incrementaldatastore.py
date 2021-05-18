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

    captured = capsys.readouterr()

    assert "The spider, database-schema and crawl-time arguments must be set." in captured.err


@pytest.mark.order(-1)
def test_invalid_spider(capsys):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'incrementaldatastore', 'non-exist-spider', 'test', 'test'])

    captured = capsys.readouterr()

    assert "The spider argument 'non-exist-spider' is not a known spider." in captured.err


@pytest.mark.order(-1)
def test_invalid_crawl_time(capsys):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'incrementaldatastore', 'fail', 'test', 'test'])

    captured = capsys.readouterr()

    assert "The crawl-time argument 'test' must be in YYYY-MM-DDTHH:MM:SS format: time data 'test' " \
           "does not match format '%Y-%m-%dT%H:%M:%S'" in captured.err


def test_format_date():
    command = IncrementalDataStore()
    assert command.format_from_date('2020-01-01T00:00:00', 'datetime') == '2020-01-01T00:00:00'
    assert command.format_from_date('2020-01-01T00:00:00', 'date') == '2020-01-01'
    assert command.format_from_date('2020-01-01T00:00:00', 'year-month') == '2020-01'
    assert command.format_from_date('2020-01-01T00:00:00', 'year') == '2020'


@patch('scrapy.crawler.CrawlerProcess.crawl')
@pytest.mark.order(-1)
def test_command(crawl, caplog, tmpdir):

    release_date = '2020-05-13T00:00:00Z'
    crawl_date = '2020-01-01T00:00:00'

    data_directory = os.path.join(tmpdir, 'fail', '20200101_000000')
    os.makedirs(data_directory)

    with open(os.path.join(data_directory,  'data.json'), 'w') as f:
        json.dump({'releases': [{'date': release_date}]}, f)

    settings = get_project_settings()
    settings['FILES_STORE'] = tmpdir.strpath

    connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
    cursor = connection.cursor()

    with pytest.raises(SystemExit):
        execute(['scrapy', 'incrementaldatastore', 'fail', 'public', crawl_date], settings=settings)

    cursor.execute("SELECT max(data->>'date') FROM fail")
    from_date = cursor.fetchone()[0]

    assert from_date == release_date

    log = ' '.join([str(elem) for elem in caplog.records])

    assert 'Replacing the JSON data in the SQL table' in log
    assert f'Running: scrapy crawl fail -a crawl_time={crawl_date}' in log

    cursor.execute('DROP TABLE fail')
    connection.commit()
    cursor.close()
    connection.close()
