# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals

import os
import pathlib

import jsonref as jsonref
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator

from kingfisher_scrapy.items import File, FileItem


class Validate:
    def __init__(self):
        self.validators = {}
        self.files = set()
        self.file_items = set()
        schema_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)), 'item_schema')
        for item in ['File', 'FileError', 'FileItem']:
            filename = os.path.join(schema_path, f'{item}.json')
            with open(filename) as f:
                schema = jsonref.load(f, base_uri=pathlib.Path(schema_path, 'item_schema').as_uri())
            self.validators[item] = Draft4Validator(schema, format_checker=FormatChecker())

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
