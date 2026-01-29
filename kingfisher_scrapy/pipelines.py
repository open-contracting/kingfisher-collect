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
from scrapy.utils.defer import deferred_from_coro

from kingfisher_scrapy.items import File, FileItem, PluckedItem
from kingfisher_scrapy.util import transcode


class BasePipeline:
    """Base class for pipelines that need access to the spider instance."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.spider = crawler.spider

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


# https://docs.scrapy.org/en/latest/topics/item-pipeline.html#duplicates-filter
class Validate:
    """Drops duplicate files based on ``file_name`` and file items based on ``file_name`` and ``number``."""

    def __init__(self):
        self.files = set()
        self.file_items = set()

    def process_item(self, item):
        if isinstance(item, FileItem):
            key = (item.file_name, item.number)
            if key in self.file_items:
                raise DropItem(f"Duplicate FileItem: {key!r}")
            self.file_items.add(key)
        elif isinstance(item, File):
            key = item.file_name
            if key in self.files:
                raise DropItem(f"Duplicate File: {key!r}")
            self.files.add(key)

        return item


class Sample(BasePipeline):
    """Drops items and closes the spider once the sample size is reached."""

    def __init__(self, crawler):
        super().__init__(crawler)
        self.item_count = 0

    def process_item(self, item):
        if not self.spider.sample:
            return item

        if self.item_count >= self.spider.sample:
            # See scrapyextensions/closespider.py and the docstring for scrapy.utils.defer._schedule_coro().
            deferred_from_coro(self.crawler.engine.close_spider_async(reason="sample"))
            raise DropItem("Sample: Maximum sample size reached")

        self.item_count += 1
        return item


class Pluck(BasePipeline):
    """Extracts a value from the item and returns it as a plucked item."""

    def process_item(self, item):
        if not self.spider.pluck:
            return item

        value = None
        if self.spider.pluck_package_pointer:
            pointer = self.spider.pluck_package_pointer
            if isinstance(item.data, dict):
                value = _resolve_pointer(item.data, pointer)
            else:
                try:
                    value = next(transcode(self.spider, ijson.items, item.data, pointer[1:].replace("/", ".")))
                except StopIteration:
                    value = f"error: {pointer} not found"
                except ijson.common.IncompleteJSONError as e:
                    message = str(e).split("\n", 1)[0]
                    if message.endswith(
                        (
                            # Python backend.
                            "Incomplete JSON content",
                            # The JSON text can be truncated by a `bytes_received` handler.
                            "premature EOF",
                            # These messages occur if the JSON text is truncated at `"\\u` or `"\\`.
                            r"lexical error: invalid (non-hex) character occurs after '\u' inside string.",
                            r"lexical error: inside a string, '\' occurs before a character which it may not.",
                        )
                    ):
                        value = f"error: {pointer} not found within initial bytes"
                    else:
                        raise
        else:  # self.spider.pluck_release_pointer
            data = item.data if isinstance(item.data, dict) else json.loads(item.data)

            if item.data_type.startswith("release"):
                releases = data["releases"]
                if releases:
                    value = max(_resolve_pointer(r, self.spider.pluck_release_pointer) for r in releases)
            elif item.data_type.startswith("record"):
                records = data["records"]
                if records:
                    # This assumes that the first record in the record package has the desired value.
                    record = records[0]
                    if "releases" in record:
                        value = max(_resolve_pointer(r, self.spider.pluck_release_pointer) for r in record["releases"])
                    elif "compiledRelease" in record:
                        value = _resolve_pointer(record["compiledRelease"], self.spider.pluck_release_pointer)

        if value and self.spider.pluck_truncate:
            value = value[: self.spider.pluck_truncate]

        return PluckedItem(value=value)


class Unflatten(BasePipeline):
    """Converts an item's data from CSV/XLSX to JSON, using the ``unflatten`` command from Flatten Tool."""

    def process_item(self, item):
        if not self.spider.unflatten or not isinstance(item, File | FileItem):
            return item

        input_name = item.file_name

        # For example, uganda_releases previously yielded either JSON or XLSX, using the same URL pattern.
        if input_name.endswith(".json"):
            if item.data.startswith(b"PK\x03\x04"):
                input_name = f"{os.path.splitext(input_name)[0]}.xlsx"
            else:
                return item

        if input_name.endswith(".csv"):
            item.file_name = f"{item.file_name[:-4]}.json"
            input_format = "csv"
        elif input_name.endswith(".xlsx"):
            item.file_name = f"{item.file_name[:-5]}.json"
            input_format = "xlsx"
        else:
            extension = os.path.splitext(input_name)[1]
            raise NotSupported(f"Unsupported extension '{extension}' of {input_name} from {item.url}")

        with tempfile.TemporaryDirectory() as directory:
            input_path = os.path.join(directory, input_name)
            output_name = os.path.join(directory, item.file_name)
            if input_format == "csv":
                input_name = directory
            elif input_format == "xlsx":
                input_name = input_path

            with open(input_path, "wb") as f:
                f.write(item.data)

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FlattenToolWarning)

                unflatten(
                    input_name,
                    root_list_path="releases",
                    root_id="ocid",
                    schema=json.loads(
                        pkgutil.get_data("kingfisher_scrapy", f"schema/{self.spider.ocds_version}.json")
                    ),
                    input_format=input_format,
                    output_name=output_name,
                    **self.spider.unflatten_args,
                )

            with open(output_name, "rb") as f:
                item.data = f.read()

        return item


def _resolve_pointer(data, pointer):
    try:
        return jsonpointer.resolve_pointer(data, pointer)
    except jsonpointer.JsonPointerException:
        return f"error: {pointer} not found"
