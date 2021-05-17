import os
import sys
from subprocess import Popen, PIPE

import psycopg2
import pytest
from scrapy.cmdline import execute
from kingfisher_scrapy.commands.incrementaldatastore import IncrementalDataStore


# tests/extensions/test_kingfisher_process_api.py fails if execute() is already called.
@pytest.mark.order(-1)
def test_command_without_arguments(caplog):
    with pytest.raises(SystemExit) as e:
        execute(['scrapy', 'incrementaldatastore'])

    assert e.value.code == 2


@pytest.mark.order(-1)
def test_invalid_spider(caplog):
    with pytest.raises(SystemExit) as e:
        execute(['scrapy', 'incrementaldatastore', 'non-exist-spider', 'test', 'test'])
    assert e.value.code == 2


@pytest.mark.order(-1)
def test_invalid_crawl_time(caplog):
    with pytest.raises(SystemExit) as e:
        execute(['scrapy', 'incrementaldatastore', 'succeed', 'test', 'test'])
    assert e.value.code == 2


def test_format_date():
    command = IncrementalDataStore()
    assert command.format_from_date('2020-01-01T00:00:00', 'datetime') == '2020-01-01T00:00:00'
    assert command.format_from_date('2020-01-01T00:00:00', 'date') == '2020-01-01'
    assert command.format_from_date('2020-01-01T00:00:00', 'year-month') == '2020-01'
    assert command.format_from_date('2020-01-01T00:00:00', 'year') == '2020'


# from https://github.com/scrapy/scrapy/blob/master/tests/test_commands.py
def test_command(caplog):

    connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
    cursor = connection.cursor()
    os.environ['FILE_STORE'] = '/tmp/data'
    args = (sys.executable, '-m', 'scrapy.cmdline', 'incrementaldatastore', 'succeed', 'public', '2021-05-13T00:00:00')
    cwd = os.path.dirname(os.path.abspath(__file__))
    proc = Popen(args, stdout=PIPE, stderr=PIPE, cwd=cwd)
    stdout, stderr = proc.communicate()
    assert stdout == b''
    assert b'Replacing the JSON data in the SQL table' in stderr
    assert b'Running: scrapy crawl succeed -a crawl_time=2021-05-13T00:00:00' in stderr

    proc = Popen(args, stdout=PIPE, stderr=PIPE, cwd=cwd)
    stdout, stderr = proc.communicate()

    assert b'Running: scrapy crawl succeed -a crawl_time=2021-05-13T00:00:00 -a from_date=2020-05-13\n' in stderr

    cursor.execute('DROP TABLE succeed')
    connection.commit()
    cursor.close()
    connection.close()
