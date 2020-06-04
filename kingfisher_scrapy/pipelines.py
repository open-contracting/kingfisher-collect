# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json

from kingfisher_scrapy.items import FileItem, File, LatestReleaseDateItem


class Validate:
    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            # We call this in the item pipeline to guarantee that all items are validated. However, its backtrace isn't
            # as helpful for debugging, so we could also call it in ``BaseSpider`` if this becomes an issue.
            item.validate()

        return item


class LatestReleaseDate:
    def process_item(self, item, spider):
        if spider.last and (isinstance(item, FileItem) or isinstance(item, File)):
            if item['data_type'] == 'release_package'\
                    or item['data_type'] == 'record_package':
                return LatestReleaseDateItem({
                    'date': json.loads(item['data'])['releases'][0]['date']
                })
