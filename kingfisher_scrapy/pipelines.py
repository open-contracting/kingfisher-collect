# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import os
import pkgutil
import tempfile

import jsonpointer
from flattentool import unflatten
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator, RefResolver
from ocdsmerge.util import get_release_schema_url, get_tags
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileItem, PluckedItem


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
                spider.logger.warning('Duplicate FileItem: %r', key)
            self.file_items.add(key)
        elif isinstance(item, File):
            key = item['file_name']
            if key in self.files:
                spider.logger.warning('Duplicate File: %r', key)
            self.files.add(key)

        return item


class Sample:
    """
    Drop items and close the spider once the sample size is reached.
    """
    def __init__(self):
        self.item_count = 0

    def process_item(self, item, spider):
        if not spider.sample:
            return item

        # Drop FileError items, so that we keep trying to get data.
        if not isinstance(item, (File, FileItem)):
            raise DropItem('Item is not a File or FileItem')
        if self.item_count >= spider.sample:
            spider.crawler.engine.close_spider(spider, 'sample')
            raise DropItem('Maximum sample size reached')

        self.item_count += 1
        return item

    def open_spider(self, spider):
        if spider.sample:
            spider.crawler.engine.downloader.total_concurrency = 1


class Pluck:
    def process_item(self, item, spider):
        if not spider.pluck:
            return item

        value = None
        if spider.package_pointer:
            try:
                package = _get_package(item)
            except NotImplementedError as e:
                value = f'error: {e}'
            else:
                value = _resolve_pointer(package, spider.package_pointer)
        else:  # spider.release_pointer
            if item['data_type'] in ('release_package', 'release_package_list', 'release_package_list_in_results',
                                     'release_list', 'release'):
                data = _get_releases(item)
                if data:
                    value = max(_resolve_pointer(r, spider.release_pointer) for r in data)
            elif item['data_type'] in ('record_package', 'record_package_list', 'record_package_list_in_results',
                                       'record'):
                data = _get_records(item)
                if data:
                    # This assumes that the first record in the record package has the desired value.
                    data = data[0]
                    if 'releases' in data:
                        value = max(_resolve_pointer(r, spider.release_pointer) for r in data['releases'])
                    elif 'compiledRelease' in data:
                        value = _resolve_pointer(data['compiledRelease'], spider.release_pointer)

        if value and spider.truncate:
            value = value[:spider.truncate]

        return PluckedItem({'value': value})


class Unflatten:
    def process_item(self, item, spider):
        if not spider.unflatten:
            return item

        input_name = item['file_name']
        if input_name.endswith('.csv'):
            item['file_name'] = item['file_name'][:-4] + '.json'
            input_format = 'csv'
        elif input_name.endswith('.xlsx'):
            item['file_name'] = item['file_name'][:-5] + '.json'
            input_format = 'xlsx'
        else:
            raise NotImplementedError(f"the file '{input_name}' has no extension or is not CSV or XLSX, "
                                      f"obtained from: {item['url']}")

        spider_ocds_version = spider.ocds_version.replace('.', '__')
        for tag in reversed(get_tags()):
            if tag.startswith(spider_ocds_version):
                schema = get_release_schema_url(tag)
                break
        else:
            raise NotImplementedError(f"no schema found for '{spider_ocds_version}'")

        with tempfile.TemporaryDirectory() as directory:
            input_path = os.path.join(directory, input_name)
            output_name = os.path.join(directory, item['file_name'])
            if input_format == 'csv':
                input_name = directory
            elif input_format == 'xlsx':
                input_name = input_path

            with open(input_path, 'wb') as f:
                f.write(item['data'])

            unflatten(
                input_name,
                root_list_path='releases',
                root_id='ocid',
                schema=schema,
                input_format=input_format,
                output_name=output_name
            )

            with open(output_name, 'r') as f:
                item['data'] = f.read()

        return item


def _resolve_pointer(data, pointer):
    try:
        return jsonpointer.resolve_pointer(data, pointer)
    except jsonpointer.JsonPointerException:
        return f'error: {pointer} not found'


def _get_package(item):
    data = json.loads(item['data'])

    if item['data_type'] in ('release_package', 'record_package'):
        return data
    # This assumes that the first package in the list has the desired value.
    elif item['data_type'] in ('release_package_list', 'record_package_list'):
        return data[0]
    elif item['data_type'] in ('release_package_list_in_results', 'record_package_list_in_results'):
        return data['results'][0]

    raise NotImplementedError(f"no package for data_type: {item['data_type']}")


def _get_releases(item):
    data = json.loads(item['data'])

    if item['data_type'] == 'release_package':
        return data['releases']
    # This assumes that the first package in the list has the desired value.
    elif item['data_type'] == 'release_package_list':
        return data[0]['releases']
    elif item['data_type'] == 'release_package_list_in_results':
        return data['results'][0]['releases']
    elif item['data_type'] == 'release_list':
        return data
    elif item['data_type'] == 'release':
        return [data]

    raise NotImplementedError(f"unhandled data_type: {item['data_type']}")


def _get_records(item):
    data = json.loads(item['data'])

    if item['data_type'] == 'record_package':
        return data['records']
    # This assumes that the first package in the list has the desired value.
    elif item['data_type'] == 'record_package_list':
        return data[0]['records']
    elif item['data_type'] == 'record_package_list_in_results':
        return data['results'][0]['records']
    elif item['data_type'] == 'record':
        return [data]

    raise NotImplementedError(f"unhandled data_type: {item['data_type']}")
