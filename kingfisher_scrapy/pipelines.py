# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import pkgutil

from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator, RefResolver

from kingfisher_scrapy.items import File, FileItem


def _json_loads(basename):
    return json.loads(pkgutil.get_data('kingfisher_scrapy', f'item_schema/{basename}.json'))


class Validate:
    def __init__(self):
        self.validators = {}
        self.files = set()
        self.file_items = set()

        resolver = RefResolver.from_schema(_json_loads('item'))
        checker = FormatChecker()
        for item in ('File', 'FileError', 'FileItem'):
            self.validators[item] = Draft4Validator(_json_loads(item), resolver=resolver, format_checker=checker)

    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            self.validators.get(item.__class__.__name__).validate(dict(item))

        if isinstance(item, FileItem):
            key = (item['file_name'], item['number'])
            if key in self.file_items:
                spider.logger.warning('Duplicate FileItem: {!r}'.format(key))
            self.file_items.add(key)
        elif isinstance(item, File):
            key = item['file_name']
            if key in self.files:
                spider.logger.warning('Duplicate File: {!r}'.format(key))
            self.files.add(key)

        return item
