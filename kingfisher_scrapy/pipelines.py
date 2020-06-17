# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
from kingfisher_scrapy.items import File, FileItem


class Validate:
    def __init__(self):
        self.file_names = set()
        self.file_items = set()

    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            # We call this in the item pipeline to guarantee that all items are validated. However, its backtrace isn't
            # as helpful for debugging, so we could also call it in ``BaseSpider`` if this becomes an issue.
            item.validate()

        if isinstance(item, FileItem):
            if (item['file_name'], item['number']) in self.file_items:
                spider.logger.warning('Duplicated filename and number pair: {}-{}'.format(item['file_name'],
                                                                                          item['number']))
            self.file_items.add((item['file_name'], item['number']))
        elif isinstance(item, File):
            if item['file_name'] in self.file_names:
                spider.logger.warning('Duplicated filename: {}'.format(item['file_name']))
            self.file_names.add(item['file_name'])

        return item
