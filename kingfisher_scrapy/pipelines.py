# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json
import os
import pkgutil
import tempfile
import warnings

import ijson
import jsonpointer
from flattentool import unflatten
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator
from ocdsmerge.util import get_release_schema_url, get_tags
from referencing import Registry, Resource
from scrapy.exceptions import DropItem, NotSupported

from kingfisher_scrapy.items import File, FileItem, PluckedItem
from kingfisher_scrapy.util import transcode


def _json_loads(basename):
    return json.loads(pkgutil.get_data('kingfisher_scrapy', f'item_schema/{basename}.json'))


class Validate:
    """
    Drops duplicate files based on ``file_name`` and file items based on ``file_name`` and ``number``.

    :raises jsonschema.ValidationError: if the item is invalid
    """

    def __init__(self):
        self.validators = {}
        self.files = set()
        self.file_items = set()

        schema = Resource.from_contents(_json_loads('item'))
        registry = Registry().with_resource('urn:item', schema)
        checker = FormatChecker()
        for item in ('File', 'FileError', 'FileItem'):
            self.validators[item] = Draft4Validator(_json_loads(item), registry=registry, format_checker=checker)

    def process_item(self, item, spider):
        if hasattr(item, 'validate'):
            self.validators.get(item.__class__.__name__).validate(dict(item))

        if isinstance(item, FileItem):
            key = (item['file_name'], item['number'])
            if key in self.file_items:
                raise DropItem(f'Duplicate FileItem: {key!r}')
            self.file_items.add(key)
        elif isinstance(item, File):
            key = item['file_name']
            if key in self.files:
                raise DropItem(f'Duplicate File: {key!r}')
            self.files.add(key)

        return item


class Sample:
    """
    Drops items and closes the spider once the sample size is reached.
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
    """
    Extracts a value from the item and returns it as a plucked item.
    """

    def process_item(self, item, spider):
        if not spider.pluck:
            return item

        value = None
        if spider.pluck_package_pointer:
            pointer = spider.pluck_package_pointer
            if isinstance(item['data'], dict):
                value = _resolve_pointer(item['data'], pointer)
            else:
                try:
                    value = next(transcode(spider, ijson.items, item['data'], pointer[1:].replace('/', '.')))
                except StopIteration:
                    value = f'error: {pointer} not found'
                except ijson.common.IncompleteJSONError as e:
                    message = str(e).split('\n', 1)[0]
                    if message.endswith((
                        # Python backend.
                        'Incomplete JSON content',
                        # The JSON text can be truncated by a `bytes_received` handler.
                        'premature EOF',
                        # These messages occur if the JSON text is truncated at `"\\u` or `"\\`.
                        r"lexical error: invalid (non-hex) character occurs after '\u' inside string.",
                        r"lexical error: inside a string, '\' occurs before a character which it may not.",
                    )):
                        value = f'error: {pointer} not found within initial bytes'
                    else:
                        raise
        else:  # spider.pluck_release_pointer
            if isinstance(item['data'], dict):
                data = item['data']
            else:
                data = json.loads(item['data'])

            if item['data_type'].startswith('release'):
                releases = data['releases']
                if releases:
                    value = max(_resolve_pointer(r, spider.pluck_release_pointer) for r in releases)
            elif item['data_type'].startswith('record'):
                records = data['records']
                if records:
                    # This assumes that the first record in the record package has the desired value.
                    record = records[0]
                    if 'releases' in record:
                        value = max(_resolve_pointer(r, spider.pluck_release_pointer) for r in record['releases'])
                    elif 'compiledRelease' in record:
                        value = _resolve_pointer(record['compiledRelease'], spider.pluck_release_pointer)

        if value and spider.pluck_truncate:
            value = value[:spider.pluck_truncate]

        return PluckedItem({'value': value})


class Unflatten:
    """
    Converts an item's data from CSV/XLSX to JSON, using the ``unflatten`` command from Flatten Tool.
    """

    def process_item(self, item, spider):
        if not spider.unflatten or not isinstance(item, (File, FileItem)):
            return item

        input_name = item['file_name']
        if input_name.endswith('.csv'):
            item['file_name'] = f'{item["file_name"][:-4]}.json'
            input_format = 'csv'
        elif input_name.endswith('.xlsx'):
            item['file_name'] = f'{item["file_name"][:-5]}.json'
            input_format = 'xlsx'
        else:
            extension = os.path.splitext(input_name)[1]
            raise NotSupported(f"Unsupported extension '{extension}' of {input_name} from {item['url']}")

        spider_ocds_version = spider.ocds_version.replace('.', '__')
        for tag in reversed(get_tags()):
            if tag.startswith(spider_ocds_version):
                schema = get_release_schema_url(tag)
                break
        else:
            raise NotSupported(f"Unsupported version '{spider_ocds_version}' from {spider.ocds_version}")

        with tempfile.TemporaryDirectory() as directory:
            input_path = os.path.join(directory, input_name)
            output_name = os.path.join(directory, item['file_name'])
            if input_format == 'csv':
                input_name = directory
            elif input_format == 'xlsx':
                input_name = input_path

            with open(input_path, 'wb') as f:
                f.write(item['data'])

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')  # flattentool uses UserWarning, so we can't set a specific category

                unflatten(
                    input_name,
                    root_list_path='releases',
                    root_id='ocid',
                    schema=schema,
                    input_format=input_format,
                    output_name=output_name,
                    **spider.unflatten_args
                )

            with open(output_name, 'r') as f:
                item['data'] = f.read()

        return item


def _resolve_pointer(data, pointer):
    try:
        return jsonpointer.resolve_pointer(data, pointer)
    except jsonpointer.JsonPointerException:
        return f'error: {pointer} not found'
