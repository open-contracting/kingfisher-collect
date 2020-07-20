# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import pkgutil

from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator, RefResolver
from scrapy.exceptions import DropItem

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
        # Skip this pipeline stage unless the spider is explicitly configured to get the latest release date.
        if not spider.latest:
            return item

        # Drop any extra items that are yielded before the spider closes.
        if spider.name in self.processed:
            spider.crawler.engine.close_spider(spider, reason='processed')
            raise DropItem()

        # Drop FileError items, so that we keep trying to get data.
        if not isinstance(item, (File, FileItem)):
            raise DropItem()

        date = None
        data = json.loads(item['data'])

        if item['data_type'] in ('release_package', 'release_package_list', 'release_package_list_in_results',
                                 'release_list', 'release', 'compiled_release'):
            if item['data_type'] == 'release_package':
                data = data['releases']
            elif item['data_type'] == 'release_package_list':
                data = data[0]['releases']
            elif item['data_type'] == 'release_package_list_in_results':
                data = data['results'][0]['releases']
            if data:
                if item['data_type'] in ('release', 'compiled_release'):
                    date = data['date']
                else:
                    date = max(r['date'] for r in data)
        elif item['data_type'] in ('record_package', 'record_package_list', 'record_package_list_in_results',
                                   'record_list', 'record'):
            if item['data_type'] == 'record_package':
                data = data['records']
            elif item['data_type'] == 'record_package_list':
                data = data[0]['records']
            elif item['data_type'] == 'record_package_list_in_results':
                data = data['results'][0]['records']
            elif item['data_type'] == 'record':
                data = [data]
            if data:
                # This assumes that the first record in the record package has the most recent date.
                data = data[0]
                if 'releases' in data:
                    date = max(r['date'] for r in data['releases'])
                elif 'compiledRelease' in data:
                    date = data['compiledRelease']['date']

        self.processed.add(spider.name)

        if date:
            date = date[:10]

        return LatestReleaseDateItem({'date': date})
