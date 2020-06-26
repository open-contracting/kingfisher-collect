# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import pkgutil

from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator, RefResolver

from kingfisher_scrapy.items import File, FileItem


class Validate:
    def __init__(self):
        package_name = 'kingfisher_scrapy'
        schema_dir = 'item_schema'
        self.validators = {}
        self.files = set()
        self.file_items = set()
        base_json = json.loads(pkgutil.get_data(package_name, f'{schema_dir}/item.json'))
        resolver = RefResolver.from_schema(base_json)
        for item in ('File', 'FileError', 'FileItem'):
            f = pkgutil.get_data(package_name, f'{schema_dir}/{item}.json')
            relative_schema = json.loads(f)
            self.validators[item] = Draft4Validator(relative_schema,
                                                    resolver=resolver, format_checker=FormatChecker())

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
