# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals


class Validate:
    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            # We call this in the item pipeline to guarantee that all items are validated. However, its backtrace isn't
            # as helpful for debugging, so we could also call it in ``BaseSpider`` if this becomes an issue.
            item.validate()

        return item
