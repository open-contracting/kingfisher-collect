# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json

from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import FileItem, File, LatestReleaseDateItem


class Validate:
    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            # We call this in the item pipeline to guarantee that all items are validated. However, its backtrace isn't
            # as helpful for debugging, so we could also call it in ``BaseSpider`` if this becomes an issue.
            item.validate()

        return item


class LatestReleaseDate:
    def __init__(self):
        self.processed = set()

    def process_item(self, item, spider):
        if spider.latest and (isinstance(item, FileItem) or isinstance(item, File)):
            if spider.name in self.processed:
                spider.crawler.engine.close_spider(self, reason='proccesed')
            date = None
            data = json.loads(item['data'])
            if item['data_type'] == 'release_package':
                date = data['releases'][0]['date']
            elif item['data_type'] == 'record_package':
                if 'releases' in data:
                    date = data['releases'][0]['date']
                elif 'compiledRelease' in data:
                    date = data['releases'][0]['date']
            elif item['data_type'] == 'release':
                date = data['date']
            self.processed.add(spider.name)
            return LatestReleaseDateItem({
                'date': date
            })
        else:
            return item
