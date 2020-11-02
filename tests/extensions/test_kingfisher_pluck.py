import os
from glob import glob
from tempfile import TemporaryDirectory

from kingfisher_scrapy.extensions import KingfisherPluck
from kingfisher_scrapy.items import PluckedItem
from tests import spider_with_crawler


def test_disabled():
    spider = spider_with_crawler()

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_PLUCK_PATH'] = tmpdirname
        extension = KingfisherPluck.from_crawler(spider.crawler)
        item = PluckedItem({'value': '2020-10-01'})

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, 'itemcount')

        assert not glob(os.path.join(tmpdirname, 'pluck*.csv'))


def test_item_scraped():
    spider = spider_with_crawler(release_pointer='/date')

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_PLUCK_PATH'] = tmpdirname
        extension = KingfisherPluck.from_crawler(spider.crawler)
        item = PluckedItem({'value': '2020-10-01'})

        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n' == f.read()

        # Only one item from the same spider is written.
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n' == f.read()

        # An item from another spider is appended.
        spider.name = 'other'
        item['value'] = '2020-10-02'
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n2020-10-02,other\n' == f.read()


def test_spider_closed_with_items():
    spider = spider_with_crawler(release_pointer='/date')

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_PLUCK_PATH'] = tmpdirname
        extension = KingfisherPluck.from_crawler(spider.crawler)
        item = PluckedItem({'value': '2020-10-01'})

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert '2020-10-01,test\n' == f.read()


def test_spider_closed_without_items():
    spider = spider_with_crawler(release_pointer='/date')

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_PLUCK_PATH'] = tmpdirname
        extension = KingfisherPluck.from_crawler(spider.crawler)

        extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'pluck-release-date.csv')) as f:
            assert 'closed: itemcount,test\n' == f.read()
