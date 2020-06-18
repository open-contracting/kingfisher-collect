# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import os

from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator


class Validate:
    def __init__(self):
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, 'item_schema.json')
        with open(filename) as f:
            schema = json.load(f)

        self.validator = Draft4Validator(schema, format_checker=FormatChecker())

    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            # We call this in the item pipeline to guarantee that all items are validated. However, its backtrace isn't
            # as helpful for debugging, so we could also call it in ``BaseSpider`` if this becomes an issue.
            item_str = json.dumps(item.__dict__)
            json_item = json.loads(item_str)['_values']
            print(json_item)
            self.validator.validate(json_item)
        return item
