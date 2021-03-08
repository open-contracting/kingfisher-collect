import os
from unittest.mock import MagicMock

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import KingfisherFilesStore, KingfisherProcessNGAPI
from tests import spider_with_crawler, spider_with_files_store


class Response(object):
    pass


def test_from_crawler():
    spider = spider_with_crawler(settings={
        'KINGFISHER_NG_API_URL': 'http://httpbin.org/anything',
        'KINGFISHER_NG_API_USERNAME': 'xxx',
        'KINGFISHER_NG_API_PASSWORD': 'password',
    })

    extension = KingfisherProcessNGAPI.from_crawler(spider.crawler)

    assert extension.username == 'xxx'
    assert extension.password == 'password'
    assert extension.url == 'http://httpbin.org/anything'


def test_from_crawler_missing_uri():
    spider = spider_with_crawler(settings={
        "KINGFISHER_API_URL": "missign",
        "KINGFISHER_NG_API_USERNAME": "aaa",
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessNGAPI.from_crawler(spider.crawler)

    assert str(excinfo.value) == "KINGFISHER_NG_API_URL is not set."


def test_from_crawler_missing_password():
    spider = spider_with_crawler(settings={
        "KINGFISHER_NG_API_URL": "/some/uti",
        "KINGFISHER_NG_API_USERNAME": "aaa",
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessNGAPI.from_crawler(spider.crawler)

    assert str(excinfo.value) == "Both KINGFISHER_NG_API_USERNAME and KINGFISHER_NG_API_PASSWORD must be set."


def mocked_spider_open(cls, *args, **kwargs):
    # Your custom testing override
    return 1


def test_spider_opened(tmpdir):
    spider = spider_with_files_store(tmpdir, settings={
        'KINGFISHER_NG_API_URL': 'anything',
        'KINGFISHER_NG_API_USERNAME': 'xxx',
        'KINGFISHER_NG_API_PASSWORD': 'password',
    })

    extension = KingfisherProcessNGAPI.from_crawler(spider.crawler)

    response = Response()
    response.ok = True
    response.text = '{"collection_id":"1"}'

    extension._post = MagicMock(return_value=response)
    extension.spider_opened(spider)

    extension._post.assert_called_with('api/v1/create_collection',
                                       {
                                            'source_id': 'test',
                                            'data_version': '2001-02-03 04:05:06',
                                            'note': 'collected by scrapy',
                                            'sample': None,
                                            'compile': True,
                                            'upgrade': True,
                                            'check': True
                                        })


def test_spider_closed(tmpdir):
    spider = spider_with_files_store(tmpdir, settings={
        'KINGFISHER_NG_API_URL': 'anything',
        'KINGFISHER_NG_API_USERNAME': 'xxx',
        'KINGFISHER_NG_API_PASSWORD': 'password',
    })

    extension = KingfisherProcessNGAPI.from_crawler(spider.crawler)
    extension.collection_id = 1

    response = Response()
    response.ok = True
    response.text = '{"collection_id":"1"}'

    extension._post = MagicMock(return_value=response)
    extension.spider_closed(spider, "done")

    extension._post.assert_called_with('api/v1/close_collection', {'collection_id': 1})


def test_item_scraped(tmpdir):
    settings = {
        "KINGFISHER_API_LOCAL_DIRECTORY": str(tmpdir.join('xxx')),
        'KINGFISHER_NG_API_URL': 'anything',
        'KINGFISHER_NG_API_USERNAME': 'xxx',
        'KINGFISHER_NG_API_PASSWORD': 'password',
    }

    spider = spider_with_files_store(tmpdir, settings=settings)
    extension = KingfisherProcessNGAPI.from_crawler(spider.crawler)
    extension.collection_id = 1

    item = spider.build_file(
        file_name='file.json',
        url='https://example.com/remote.json',
        data=b'{"key": "value"}',
        data_type='release_package',
    )

    store_extension = KingfisherFilesStore.from_crawler(spider.crawler)
    store_extension.item_scraped(item, spider)

    response = Response()
    response.ok = True
    response.text = '{"collection_id":"1"}'

    extension._post = MagicMock(return_value=response)
    extension.item_scraped(item, spider)

    extension._post.assert_called_with('api/v1/create_collection_file',
                                       {
                                           'collection_id': 1,
                                           'path': os.path.join(item['files_store'], item['path'])})
