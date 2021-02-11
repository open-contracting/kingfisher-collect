import os
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import KingfisherFilesStore
from kingfisher_scrapy.items import FileItem
from tests import spider_with_crawler, spider_with_files_store


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler()

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherFilesStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'FILES_STORE is not set.'


@pytest.mark.parametrize('sample,path', [
    (None, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', os.path.join('test_sample', '20010203_040506', 'file.json')),
])
def test_item_scraped_with_build_file_from_response(sample, path, tmpdir):
    spider = spider_with_files_store(tmpdir, sample=sample)
    extension = KingfisherFilesStore.from_crawler(spider.crawler)

    response = Mock()
    response.body = b'{"key": "value"}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'
    response.request.meta = {'file_name': 'file.json'}

    item = spider.build_file_from_response(response, file_name='file.json', data_type='release_package',
                                           encoding='iso-8859-1')
    extension.item_scraped(item, spider)

    with open(tmpdir.join(path)) as f:
        assert f.read() == '{"key": "value"}'

    assert item['path'] == path
    assert item['files_store'] == tmpdir


@pytest.mark.parametrize('sample,path', [
    (None, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', os.path.join('test_sample', '20010203_040506', 'file.json')),
])
@pytest.mark.parametrize('data', [b'{"key": "value"}', {"key": "value"}])
def test_item_scraped_with_build_file(sample, path, data, tmpdir):
    spider = spider_with_files_store(tmpdir, sample=sample)
    extension = KingfisherFilesStore.from_crawler(spider.crawler)

    item = spider.build_file(file_name='file.json', url='https://example.com/remote.json', data=data,
                             data_type='release_package', encoding='iso-8859-1')
    extension.item_scraped(item, spider)

    with open(tmpdir.join(path)) as f:
        assert f.read() == '{"key": "value"}'

    assert item['path'] == path
    assert item['files_store'] == tmpdir


def test_item_scraped_with_build_file_and_existing_directory():
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider = spider_with_crawler(settings={'FILES_STORE': files_store})
        extension = KingfisherFilesStore.from_crawler(spider.crawler)
        item = spider.build_file(file_name='file.json', data=b'{"key": "value"}')

        os.makedirs(os.path.join(files_store, 'test', '20010203_040506'))

        # No FileExistsError exception.
        extension.item_scraped(item, spider)


def test_item_scraped_with_file_item():
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider = spider_with_crawler(settings={'FILES_STORE': files_store})
        extension = KingfisherFilesStore.from_crawler(spider.crawler)
        item = FileItem({'number': 1, 'file_name': 'file.json', 'data': 'data'})

        assert extension.item_scraped(item, spider) is None
