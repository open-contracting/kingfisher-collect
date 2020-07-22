import os
from tempfile import TemporaryDirectory

from kingfisher_scrapy.extensions import KingfisherLatestDate
from kingfisher_scrapy.items import LatestReleaseDateItem
from tests import spider_with_crawler


def test_disabled():
    spider = spider_with_crawler()

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_LATEST_RELEASE_DATE_PATH'] = tmpdirname
        extension = KingfisherLatestDate.from_crawler(spider.crawler)
        item = LatestReleaseDateItem({'date': '2020-10-01'})

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, 'itemcount')

        assert not os.path.exists(os.path.join(tmpdirname, 'latestreleasedate.csv'))


def test_item_scraped():
    spider = spider_with_crawler(latest='true')

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_LATEST_RELEASE_DATE_PATH'] = tmpdirname
        extension = KingfisherLatestDate.from_crawler(spider.crawler)
        item = LatestReleaseDateItem({'date': '2020-10-01'})

        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'latestreleasedate.csv')) as f:
            assert '2020-10-01,test\n' == f.read()

        # Only one item from the same spider is written.
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'latestreleasedate.csv')) as f:
            assert '2020-10-01,test\n' == f.read()

        # An item from another spider is appended.
        spider.name = 'other'
        item['date'] = '2020-10-02'
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'latestreleasedate.csv')) as f:
            assert '2020-10-01,test\n2020-10-02,other\n' == f.read()


def test_spider_closed_with_items():
    spider = spider_with_crawler(latest='true')

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_LATEST_RELEASE_DATE_PATH'] = tmpdirname
        extension = KingfisherLatestDate.from_crawler(spider.crawler)
        item = LatestReleaseDateItem({'date': '2020-10-01'})

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'latestreleasedate.csv')) as f:
            assert '2020-10-01,test\n' == f.read()


def test_spider_closed_without_items():
    spider = spider_with_crawler(latest='true')

    with TemporaryDirectory() as tmpdirname:
        spider.crawler.settings['KINGFISHER_LATEST_RELEASE_DATE_PATH'] = tmpdirname
        extension = KingfisherLatestDate.from_crawler(spider.crawler)

        extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'latestreleasedate.csv')) as f:
            assert 'itemcount,test\n' == f.read()
