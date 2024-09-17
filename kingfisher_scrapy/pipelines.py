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
from flattentool.exceptions import FlattenToolWarning
from scrapy.exceptions import DropItem, NotSupported

from kingfisher_scrapy.items import File, FileItem, PluckedItem
from kingfisher_scrapy.util import transcode


# https://docs.scrapy.org/en/latest/topics/item-pipeline.html#duplicates-filter
class Validate:
    """Drops duplicate files based on ``file_name`` and file items based on ``file_name`` and ``number``."""

    def __init__(self):
        self.files = set()
        self.file_items = set()

    def process_item(self, item, spider):
        if isinstance(item, FileItem):
            key = (item.file_name, item.number)
            if key in self.file_items:
                raise DropItem(f'Duplicate FileItem: {key!r}')
            self.file_items.add(key)
        elif isinstance(item, File):
            key = item.file_name
            if key in self.files:
                raise DropItem(f'Duplicate File: {key!r}')
            self.files.add(key)

        return item


class Sample:
    """Drops items and closes the spider once the sample size is reached."""

    def __init__(self):
        self.item_count = 0

    def process_item(self, item, spider):
        if not spider.sample:
            return item

        # Drop FileError items, so that we keep trying to get data.
        if not isinstance(item, File | FileItem):
            raise DropItem(f'Sample: Item is a {type(item).__name__}, not a File or FileItem')
        if self.item_count >= spider.sample:
            spider.crawler.engine.close_spider(spider, 'sample')
            raise DropItem('Sample: Maximum sample size reached')

        self.item_count += 1
        return item

    def open_spider(self, spider):
        if spider.sample:
            spider.crawler.engine.downloader.total_concurrency = 1


class Pluck:
    """Extracts a value from the item and returns it as a plucked item."""

    def process_item(self, item, spider):
        if not spider.pluck:
            return item

        value = None
        if spider.pluck_package_pointer:
            pointer = spider.pluck_package_pointer
            if isinstance(item.data, dict):
                value = _resolve_pointer(item.data, pointer)
            else:
                try:
                    value = next(transcode(spider, ijson.items, item.data, pointer[1:].replace('/', '.')))
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
            data = item.data if isinstance(item.data, dict) else json.loads(item.data)

            if item.data_type.startswith('release'):
                releases = data['releases']
                if releases:
                    value = max(_resolve_pointer(r, spider.pluck_release_pointer) for r in releases)
            elif item.data_type.startswith('record'):
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

        return PluckedItem(value=value)


class Unflatten:
    """Converts an item's data from CSV/XLSX to JSON, using the ``unflatten`` command from Flatten Tool."""

    def process_item(self, item, spider):
        if not spider.unflatten or not isinstance(item, File | FileItem):
            return item

        input_name = item.file_name

        # uganda_releases yields JSON until 2023-2024, using the same URL pattern.
        if input_name.endswith('.json'):
            if item.data.startswith(b'PK\x03\x04'):
                input_name = f'{os.path.splitext(input_name)[0]}.xlsx'
            else:
                return item

        if input_name.endswith('.csv'):
            item.file_name = f'{item.file_name[:-4]}.json'
            input_format = 'csv'
        elif input_name.endswith('.xlsx'):
            item.file_name = f'{item.file_name[:-5]}.json'
            input_format = 'xlsx'
        else:
            extension = os.path.splitext(input_name)[1]
            raise NotSupported(f"Unsupported extension '{extension}' of {input_name} from {item.url}")

        with tempfile.TemporaryDirectory() as directory:
            input_path = os.path.join(directory, input_name)
            output_name = os.path.join(directory, item.file_name)
            schema = os.path.join(directory, 'release-schema.json')
            if input_format == 'csv':
                input_name = directory
            elif input_format == 'xlsx':
                input_name = input_path

            with open(input_path, 'wb') as f:
                f.write(item.data)
            # Flatten Tool accepts only URLs or filenames.
            with open(schema, 'wb') as f:
                f.write(pkgutil.get_data('kingfisher_scrapy', f'schema/{spider.ocds_version}.json'))

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=FlattenToolWarning)

                unflatten(
                    input_name,
                    root_list_path='releases',
                    root_id='ocid',
                    schema=schema,
                    input_format=input_format,
                    output_name=output_name,
                    **spider.unflatten_args
                )

            with open(output_name, 'rb') as f:
                item.data = f.read()

        return item


def _resolve_pointer(data, pointer):
    try:
        return jsonpointer.resolve_pointer(data, pointer)
    except jsonpointer.JsonPointerException:
        return f'error: {pointer} not found'
