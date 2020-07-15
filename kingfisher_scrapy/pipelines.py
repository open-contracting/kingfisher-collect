# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import pkgutil

from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator, RefResolver

from kingfisher_scrapy.items import File, FileItem, LatestReleaseDateItem


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


class LatestReleaseDate:
    def __init__(self):
        self.processed = set()

    def process_item(self, item, spider):
        if spider.latest and (isinstance(item, FileItem) or isinstance(item, File)):
            if spider.name in self.processed:
                spider.crawler.engine.close_spider(self, reason='proccesed')
                return
            date = None
            data = json.loads(item['data'])
            if item['data_type'] == 'release_package' or item['data_type'] == 'release' \
                    or item['data_type'] == 'release_list' or item['data_type'] == 'compiled_release'\
                    or item['data_type'] == 'release_package_list'\
                    or item['data_type'] == 'release_package_list_in_results':
                if item['data_type'] == 'release_list':
                    data = data
                elif item['data_type'] == 'release_package':
                    data = data['releases']
                elif item['data_type'] == 'release_package_list':
                    data = data[0]['releases']
                elif item['data_type'] == 'release_package_list_in_results':
                    data = data['results'][0]['releases']
                if data:
                    if item['data_type'] == 'release' or item['data_type'] == 'compiled_release':
                        date = data['date']
                    else:
                        date = max(r['date'] for r in data)
            elif item['data_type'] == 'record_package' or item['data_type'] == 'record' or \
                    item['data_type'] == 'record_list' or item['data_type'] == 'record_package_list' \
                    or item['data_type'] == 'record_package_list_in_results':
                if item['data_type'] == 'record_package':
                    data = data['records']
                elif item['data_type'] == 'record_package_list':
                    data = data[0]['records']
                elif item['data_type'] == 'record_package_list_in_results':
                    data = data['results'][0]['records']
                elif item['data_type'] == 'record_list':
                    data = data
                elif item['data_type'] == 'record':
                    data = [data]
                if data:
                    data = data[0]
                    if 'releases' in data:
                        date = max(r['date'] for r in data['releases'])
                    elif 'compiledRelease' in data:
                        date = data['compiledRelease']['date']
            self.processed.add(spider.name)
            return LatestReleaseDateItem({
                'date': date
            })
        else:
            return item
