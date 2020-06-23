# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import os
import pathlib

import jsonref as jsonref
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator


class Validate:
    def __init__(self):
        self.validators = {}
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'item_schema')
        for item in ['file', 'file_error', 'file_item']:
            filename = os.path.join(schema_path, f'{item}.json')
            with open(filename) as f:
                schema = jsonref.load(f, base_uri=pathlib.Path(os.path.join(schema_path), 'item_schema').as_uri())
            class_name = ''.join(word.title() for word in item.split('_'))
            self.validators[class_name] = Draft4Validator(schema, format_checker=FormatChecker())

    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            self.validators.get(item.__class__.__name__).validate(dict(item))
        return item
