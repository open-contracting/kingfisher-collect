from kingfisher_scrapy.extensions import ItemCount
from kingfisher_scrapy.items import FileError, FileItem
from tests import spider_with_crawler


def test_item_scraped_file(caplog):
    spider = spider_with_crawler()
    item_extension = ItemCount.from_crawler(spider.crawler)
    item = spider.build_file(
        file_name='file.json',
        url='https://example.com/remote.json',
        data_type='release_package',
        data=b'{"key": "value"}',
    )

    item_extension.item_scraped(item, spider)

    assert item_extension.stats.get_value('file_count') == 1
    assert item_extension.stats.get_value('fileitem_count', 0) == 0
    assert item_extension.stats.get_value('fileerror_count', 0) == 0


def test_item_scraped_file_item(caplog):
    spider = spider_with_crawler()
    item_extension = ItemCount.from_crawler(spider.crawler)
    item = FileItem(
        file_name='file.json',
        url='https://example.com/remote.json',
        data=b'{"key": "value"}',
        data_type='release_package',
        number=1,
    )

    item_extension.item_scraped(item, spider)

    assert item_extension.stats.get_value('fileitem_count') == 1
    assert item_extension.stats.get_value('file_count', 0) == 0
    assert item_extension.stats.get_value('fileerror_count', 0) == 0


def test_item_scraped_file_error(caplog):
    spider = spider_with_crawler()
    item_extension = ItemCount.from_crawler(spider.crawler)
    item = FileError(
        file_name='file.json',
        url='https://example.com/remote.json',
        errors={'http_code': 404},
    )

    item_extension.item_scraped(item, spider)

    assert item_extension.stats.get_value('fileerror_count') == 1
    assert item_extension.stats.get_value('file_count', 0) == 0
    assert item_extension.stats.get_value('fileitem_count', 0) == 0
